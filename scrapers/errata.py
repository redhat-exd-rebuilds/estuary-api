# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from estuary import log
from estuary.models.bugzilla import BugzillaBug
from estuary.models.errata import Advisory, ContainerAdvisory
from estuary.models.koji import ContainerKojiBuild, KojiBuild
from estuary.models.user import User
from estuary.utils.general import timestamp_to_date
from scrapers.base import BaseScraper


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
            adv = Advisory.create_or_update({
                'actual_ship_date': advisory['actual_ship_date'],
                'advisory_name': advisory['advisory_name'],
                'created_at': advisory['created_at'],
                'id_': advisory['id'],
                'issue_date': advisory['issue_date'],
                'product_name': advisory['product_name'],
                'release_date': advisory['release_date'],
                'security_impact': advisory['security_impact'],
                'security_sla': advisory['security_sla'],
                'state': advisory['state'],
                'status_time': advisory['status_time'],
                'synopsis': advisory['synopsis'],
                'update_date': advisory['update_date'],
            })[0]
            container_adv = False

            for associated_build in self.get_associated_builds(advisory['id']):
                # Even if a node has two labels in the database, Neo4j returns the node
                # only with the specific label you asked for. Hence we check for labels
                # ContainerKojiBuild and KojiBuild separately for the same node.
                build = ContainerKojiBuild.nodes.get_or_none(id_=associated_build['id_'])
                if not build:
                    build = KojiBuild.nodes.get_or_none(id_=associated_build['id_'])

                if build and not container_adv:
                    if build.__label__ == 'ContainerKojiBuild':
                        adv.add_label(ContainerAdvisory.__label__)
                        container_adv = True

                # If this is set, that means it was once part of the advisory but not anymore.
                # This relationship needs to be deleted if it exists.
                if associated_build['removed_index_id']:
                    if build:
                        adv.attached_builds.disconnect(build)
                else:
                    # Query Teiid and create the entry only if the build is not present in Neo4j
                    if not build:
                        attached_build = self.get_koji_build(associated_build['id_'])
                        if attached_build:
                            if self.is_container_build(attached_build):
                                build = ContainerKojiBuild.get_or_create(
                                    {'id_': associated_build['id_']})[0]
                            else:
                                build = KojiBuild.get_or_create(
                                    {'id_': associated_build['id_']})[0]

                    # This will happen only if we do not find the build we are looking for in Teiid
                    # which shouldn't usually happen under normal conditions
                    if not build:
                        log.warn('The Koji build with ID {} was not found in Teiid!'.format(
                            associated_build['id_']))
                        continue

                    if adv.__label__ != ContainerAdvisory.__label__ \
                            and build.__label__ == ContainerKojiBuild.__label__:
                        adv.add_label(ContainerAdvisory.__label__)

                    attached_rel = adv.attached_builds.relationship(build)
                    time_attached = associated_build['time_attached']
                    if attached_rel:
                        if attached_rel.time_attached != time_attached:
                            adv.attached_builds.replace(build, {'time_attached': time_attached})
                    else:
                        adv.attached_builds.connect(build, {'time_attached': time_attached})

            assigned_to = User.get_or_create({'username': advisory['assigned_to'].split('@')[0]})[0]
            adv.conditional_connect(adv.assigned_to, assigned_to)
            reporter = User.get_or_create({'username': advisory['reporter'].split('@')[0]})[0]
            adv.conditional_connect(adv.reporter, reporter)

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
                states.current as state,
                main.created_at,
                main.id AS id,
                main.issue_date,
                products.name as product_name,
                main.release_date,
                reporter_users.login_name AS reporter,
                main.security_impact,
                main.security_sla,
                main.status_updated_at AS status_time,
                main.synopsis,
                main.errata_type AS type,
                main.update_date
            FROM Errata_public.errata_main AS main
            LEFT JOIN Errata_public.state_indices as states
                ON main.current_state_index_id = states.id
            LEFT JOIN Errata_public.errata_products as products
                ON main.product_id = products.id
            LEFT JOIN Errata_public.users AS assigned_users
                ON main.assigned_to_id = assigned_users.id
            LEFT JOIN Errata_public.users AS reporter_users
                ON main.reporter_id = reporter_users.id
            WHERE main.update_date >= '{0}' AND main.update_date <= '{1}'
            ORDER BY main.update_date DESC;
        """.format(since, until)
        log.info('Getting Errata advisories since {0} until {1}'.format(since, until))
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
                brew_builds.version, brew_mappings.created_at as time_attached
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
                brew.build.extra,
                brew.package.name as package_name
            FROM brew.build
            LEFT JOIN brew.package ON brew.build.pkg_id = brew.package.id
            WHERE build.id = {0};
            """.format(build_id)

        result = self.teiid.query(sql)
        return result[0] if len(result) > 0 else None
