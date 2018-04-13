# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import yaml

from purview.utils.general import timestamp_to_datetime
from scrapers.base import BaseScraper
from purview import log
from purview.models.errata import Advisory, AdvisoryState
from purview.models.user import User
from purview.models.bugzilla import BugzillaBug
from purview.models.koji import KojiBuild


class ErrataScraper(BaseScraper):
    """Scrapes the Errata Tool tables in TEIID."""

    def run(self, since=None):
        """
        Run the Errata Tool scraper.

        :param str since: a datetime to start scraping data from
        """
        log.info('Starting initial load of Errata advisories')
        if since is None:
            dt_since = self.default_since
        else:
            dt_since = timestamp_to_datetime(since)
        advisories = self.get_advisories(dt_since)
        log.info('Successfully fetched {0} advisories from TEIID'.format(len(advisories)))
        self.update_neo4j(advisories)
        log.info('Initial load of Errata advisories complete!')

    def update_neo4j(self, advisories):
        """
        Update Neo4j with Errata Tool advisories from TEIID.

        :param list advisories: a list of dictionaries of advisories
        """
        count = 0
        for advisory in advisories:
            count += 1
            log.info('Processing advisory {0}/{1}'.format(count, len(advisories)))
            # The content_types column is a string with YAML in it, so convert it to a list
            content_types = yaml.safe_load(advisories[0]['content_types'])
            adv = Advisory.create_or_update({
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
            })[0]
            assigned_to = User.get_or_create({'username': advisory['assigned_to'].split('@')[0]})[0]
            adv.assigned_to.connect(assigned_to)
            assigned_to.advisories_assigned.connect(adv)
            package_owner = User.get_or_create(
                {'username': advisory['package_owner'].split('@')[0]})[0]
            adv.package_owners.connect(package_owner)
            package_owner.advisories_package_owner.connect(adv)
            reporter = User.get_or_create({'username': advisory['reporter'].split('@')[0]})[0]
            adv.reporters.connect(reporter)
            reporter.advisories_reported.connect(adv)
            reporter.advisories.connect(adv)

            for state in self.get_advisory_states(advisory['id']):
                adv_state = AdvisoryState.create_or_update({
                    'id_': state['id'],
                    'name': state['name'],
                    'created_at': state['created_at'],
                    'updated_at': state['updated_at']
                })[0]
                adv.states.connect(adv_state)
                adv_state.advisories.connect(adv)
                state_owner = User.get_or_create({'username': state['username'].split('@')[0]})[0]
                adv_state.owner.connect(state_owner)
                state_owner.advisories_state_owner.connect(adv_state)

            for attached_bug in self.get_attached_bugs(advisory['id']):
                bug = BugzillaBug.get_or_create(attached_bug)[0]
                adv.attached_bugs.connect(bug)
                bug.attached_advisories.connect(adv)

            for associated_build in self.get_associated_builds(advisory['id']):
                # If this is set, that means it was once part of the advisory but not anymore.
                # This relationship needs to be deleted if it exists.
                if associated_build['removed_index_id']:
                    build = KojiBuild.nodes.get_or_none(id_=associated_build['id_'])
                    if build:
                        adv.attached_builds.disconnect(build)
                        build.advisories.disconnect(adv)
                else:
                    # This key shouldn't be stored in Neo4j
                    del associated_build['removed_index_id']
                    build = KojiBuild.get_or_create(associated_build)[0]
                    adv.attached_builds.connect(build)
                    build.advisories.connect(adv)

    def get_advisories(self, since):
        """
        Query TEIID for the Errata Tool advisories.

        :param datetime.datetime since: determines when to start querying
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
            WHERE main.created_at >= '{0}'
            ORDER BY main.id;
        """.format(since)
        log.info('Getting Errata advisories since {0}'.format(since))
        return self.teiid.query(sql)

    def get_advisory_states(self, advisory_id):
        """
        Query TEIID to find the states of a specific advisory.

        :param int advisory_id: the advisory ID
        :return: a list of a dictionaries
        :rtype: list
        """
        sql = """\
            SELECT states.created_at, states.id, states.current as name, states.updated_at,
                users.login_name AS username
            FROM Errata_public.state_indices as states
            LEFT JOIN Errata_public.users as users ON states.who_id = users.id
            WHERE errata_id = {}
            ORDER BY states.id;
        """.format(advisory_id)
        log.info('Getting states tied to the advisory with ID {0}'.format(advisory_id))
        return self.teiid.query(sql)

    def get_associated_builds(self, advisory_id):
        """
        Query TEIID to find the Brew builds associated with a specific advisory.

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
        Query TEIID to find the Bugzilla bugs attached to a specific advisory.

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
