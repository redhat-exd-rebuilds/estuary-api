# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import yaml
import neomodel

from estuary.utils.general import timestamp_to_date
from scrapers.base import BaseScraper
from estuary import log
from estuary.models.errata import Advisory, AdvisoryState, ContainerBuildAdvisory
from estuary.models.user import User
from estuary.models.bugzilla import BugzillaBug
from estuary.models.koji import KojiBuild, ContainerKojiBuild


class ErrataScraper(BaseScraper):
    """Scrapes the Errata Tool tables in Teiid."""

    def run(self, since=None, until=None):
        """
        Run the Errata Tool scraper.

        :param str since: a datetime to start scraping data from
        :param str until: a datetime to scrape data until
        """
        log.info('Starting initial load of Errata advisories')
        if since is None:
            start_date = self.default_since
        else:
            start_date = timestamp_to_date(since)

        if until is None:
            end_date = self.default_until
        else:
            end_date = timestamp_to_date(until)
        advisories = self.get_advisories(start_date, end_date)
        log.info('Successfully fetched {0} advisories from Teiid'.format(len(advisories)))
        self.update_neo4j(advisories)
        log.info('Initial load of Errata advisories complete!')

    def update_neo4j(self, advisories):
        """
        Update Neo4j with Errata Tool advisories from Teiid.

        :param list advisories: a list of dictionaries of advisories
        """
        count = 0
        for advisory in advisories:
            count += 1
            log.info('Processing advisory {0}/{1}'.format(count, len(advisories)))
            # The content_types column is a string with YAML in it, so convert it to a list
            content_types = yaml.safe_load(advisory['content_types'])
            adv_params = {
                'actual_ship_date': advisory['actual_ship_date'],
                'advisory_name': advisory['advisory_name'],
                'content_types': content_types,
                'created_at': advisory['created_at'],
                'id_': advisory['id'],
                'issue_date': advisory['issue_date'],
                'product_name': advisory['product_name'],
                'product_short_name': advisory['product_short_name'],
                'release_date': advisory['release_date'],
                'security_impact': advisory['security_impact'],
                'security_sla': advisory['security_sla'],
                'state': advisory['state'],
                'status_time': advisory['status_time'],
                'synopsis': advisory['synopsis'],
                'type_': advisory['type'],
                'update_date': advisory['update_date'],
                'updated_at': advisory['updated_at']
            }

            associated_builds = self.get_associated_builds(advisory['id'])
            if not associated_builds:
                adv = Advisory.create_or_update(adv_params)[0]

            for associated_build in associated_builds:
                build = ContainerKojiBuild.nodes.get_or_none(id_=associated_build['id_'])
                if not build:
                    build = KojiBuild.nodes.get_or_none(id_=associated_build['id_'])

                container_adv = False
                if build:
                    if build.__label__ == 'ContainerKojiBuild':
                        adv = self.create_container_build_advisory(adv_params)
                        container_adv = True
                    else:
                        adv = Advisory.create_or_update(adv_params)[0]

                # If this is set, that means it was once part of the advisory but not anymore.
                # This relationship needs to be deleted if it exists.
                if associated_build['removed_index_id']:
                    if build:
                        adv.attached_builds.disconnect(build)
                else:
                    # This key shouldn't be stored in Neo4j
                    del associated_build['removed_index_id']
                    # Query Teiid only if the build is not present in Neo4j
                    if build:
                        if container_adv:
                            is_container_build = True
                        else:
                            is_container_build = False
                    else:
                        attached_build = self.get_koji_build(associated_build['id_'])
                        if attached_build:
                            is_container_build = self.is_container_build(attached_build)
                        else:
                            is_container_build = False

                    if is_container_build:
                        build = ContainerKojiBuild.get_or_create(
                            {'id_': associated_build['id_']})[0]
                        adv = self.create_container_build_advisory(adv_params)
                    else:
                        build = KojiBuild.get_or_create({'id_': associated_build['id_']})[0]
                        adv = Advisory.create_or_update(adv_params)[0]
                    adv.attached_builds.connect(build)

            assigned_to = User.get_or_create({'username': advisory['assigned_to'].split('@')[0]})[0]
            adv.conditional_connect(adv.assigned_to, assigned_to)
            package_owner = User.get_or_create(
                {'username': advisory['package_owner'].split('@')[0]})[0]
            adv.conditional_connect(adv.package_owner, package_owner)
            reporter = User.get_or_create({'username': advisory['reporter'].split('@')[0]})[0]
            adv.conditional_connect(adv.reporter, reporter)

            for state in self.get_advisory_states(advisory['id']):
                adv_state = AdvisoryState.create_or_update({
                    'id_': state['id'],
                    'name': state['name'],
                    'created_at': state['created_at'],
                    'updated_at': state['updated_at']
                })[0]
                adv_state.conditional_connect(adv_state.advisory, adv)
                state_creator = User.get_or_create({'username': state['username'].split('@')[0]})[0]
                adv_state.conditional_connect(adv_state.creator, state_creator)

            for attached_bug in self.get_attached_bugs(advisory['id']):
                bug = BugzillaBug.get_or_create(attached_bug)[0]
                adv.attached_bugs.connect(bug)

    def get_advisories(self, since, until):
        """
        Query Teiid for the Errata Tool advisories.

        :param datetime.datetime since: determines when to start querying
        :param datetime.datetime until: determines until when to scrape data
        :return: a list of dictionaries
        :rtype: list
        """
        sql = """\
            SELECT
                main.actual_ship_date,
                main.fulladvisory as advisory_name,
                assigned_users.login_name AS assigned_to,
                main.content_types,
                states.current as state,
                main.created_at,
                main.id AS id,
                main.issue_date,
                package_users.login_name AS package_owner,
                products.name as product_name,
                products.short_name as product_short_name,
                main.release_date,
                reporter_users.login_name AS reporter,
                main.security_impact,
                main.security_sla,
                main.status_updated_at AS status_time,
                main.synopsis,
                main.errata_type AS type,
                main.update_date,
                main.updated_at
            FROM Errata_public.errata_main AS main
            LEFT JOIN Errata_public.state_indices as states
                ON main.current_state_index_id = states.id
            LEFT JOIN Errata_public.errata_products as products
                ON main.product_id = products.id
            LEFT JOIN Errata_public.users AS assigned_users
                ON main.assigned_to_id = assigned_users.id
            LEFT JOIN Errata_public.users AS package_users
                ON main.package_owner_id = package_users.id
            LEFT JOIN Errata_public.users AS reporter_users
                ON main.reporter_id = reporter_users.id
            WHERE main.updated_at >= '{0}' AND main.updated_at <= '{1}'
            ORDER BY main.updated_at DESC;
        """.format(since, until)
        log.info('Getting Errata advisories since {0} until {1}'.format(since, until))
        return self.teiid.query(sql)

    def get_advisory_states(self, advisory_id):
        """
        Query Teiid to find the states of a specific advisory.

        :param int advisory_id: the advisory ID
        :return: a list of a dictionaries
        :rtype: list
        """
        sql = """\
            SELECT states.created_at, states.id, states.current as name, states.updated_at,
                users.login_name AS username
            FROM Errata_public.state_indices as states
            LEFT JOIN Errata_public.users as users ON states.who_id = users.id
            WHERE errata_id = {};
        """.format(advisory_id)
        log.info('Getting states tied to the advisory with ID {0}'.format(advisory_id))
        return self.teiid.query(sql)

    def get_associated_builds(self, advisory_id):
        """
        Query Teiid to find the Brew builds associated with a specific advisory.

        :param int advisory_id: the advisory ID
        :return: a list of a dictionaries
        :rtype: list
        """
        sql = """\
            SELECT brew_builds.id as id_, packages.name, brew_builds.release, removed_index_id,
                brew_builds.version
            FROM Errata_public.errata_brew_mappings as brew_mappings
            LEFT JOIN Errata_public.brew_builds AS brew_builds
                ON brew_builds.id = brew_mappings.brew_build_id
            LEFT JOIN Errata_public.packages AS packages
                ON brew_builds.package_id = packages.id WHERE errata_id = {0};
        """.format(advisory_id)
        log.info('Getting Brew builds tied to the advisory with ID {0}'.format(advisory_id))
        return self.teiid.query(sql)

    def get_attached_bugs(self, advisory_id):
        """
        Query Teiid to find the Bugzilla bugs attached to a specific advisory.

        :param int advisory_id: the advisory ID
        :return: a list of a dictionaries
        :rtype: list
        """
        sql = """\
            SELECT filed_bugs.bug_id as id_
            FROM Errata_public.filed_bugs as filed_bugs
            WHERE filed_bugs.errata_id = {0};
        """.format(advisory_id)
        log.info('Getting Bugzilla bugs tied to the advisory with ID {0}'.format(advisory_id))
        return self.teiid.query(sql)

    def get_koji_build(self, build_id):
        """
        Query Teiid to find the Koji build attached to a specific advisory.

        :param int build_id: the build ID
        :return: a list of a dictionaries
        :rtype: list
        """
        sql = """\
            SELECT
                build.extra,
                package.name as package_name
            FROM build
            LEFT JOIN package ON build.pkg_id = package.id
            WHERE build.id = {0};
            """.format(build_id)

        result = self.teiid.query(sql)
        return result[0] if len(result) > 0 else None

    def create_container_build_advisory(self, advisory_params):
        """
        Create a ContainerBuildAdvisory node in Neo4j and remove duplicates if present.

        :param dict advisory_params: parameters for a ContainerBuildAdvisory
        :return: Neo4j object
        :rtype: ContainerBuildAdvisory
        """
        try:
            adv = ContainerBuildAdvisory.create_or_update(advisory_params)[0]
        except neomodel.exceptions.ConstraintValidationFailed:
            # This must have errantly been created as an Advisory instead of a
            # ContainerBuildAdvisory, so let's fix that.
            adv = Advisory.nodes.get_or_none(id_=advisory_params['id_'])
            if not adv:
                # If there was a constraint validation failure and the build isn't just the
                # wrong label, then we can't recover.
                raise
            adv.add_label(ContainerBuildAdvisory.__label__)
            adv = ContainerBuildAdvisory.create_or_update(advisory_params)[0]
        return adv
