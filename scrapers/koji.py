# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import xml.etree.ElementTree as ET
import json

import neomodel

from scrapers.base import BaseScraper
from estuary.models.koji import ContainerKojiBuild, KojiBuild, KojiTag, ModuleKojiBuild
from estuary.models.user import User
from estuary.models.distgit import DistGitCommit
import estuary.utils.general as utils
from estuary import log


class KojiScraper(BaseScraper):
    """Scrapes the Koji tables in Teiid."""

    def run(self, since=None, until=None):
        """
        Run the Koji scraper.

        :param str since: a datetime to start scraping data from
        :param str until: a datetime to scrape data until
        """
        log.info('Starting initial load for Koji')
        # Initialize a start date from which all builds must be fetched
        # If no input is given by the user, fetch builds from the past two years
        if since is None:
            start_date = self.default_since
        else:
            start_date = utils.timestamp_to_date(since)

        if until is None:
            end_date = self.default_until
        else:
            end_date = utils.timestamp_to_date(until)
        builds = self.get_koji_builds(start_date, end_date)
        log.info('Successfully fetched {0} builds from teiid'.format(len(builds)))
        self.update_neo4j(builds)
        log.info('Initial load of Koji builds complete!')

    def get_koji_builds(self, start_date, end_date):
        """
        Query Teiid for Koji builds.

        :param datetime.datetime start_date: determines when to start the query
        :param datetime.datetime end_date: determines until when to scrape data
        :return: a list of dictionaries
        :rtype: list
        """
        # SQL query to fetch all builds from start date until now
        log.info('Getting all Koji builds since {0} until {1}'.format(start_date, end_date))
        sql_query = """
            SELECT
                brew.events.time as creation_time,
                brew.build.completion_time,
                brew.build.epoch,
                brew.build.extra,
                brew.build.id,
                brew.users.name as owner_name,
                brew.package.name as package_name,
                brew.build.release,
                brew.build.start_time,
                brew.build.state,
                brew.build.task_id,
                brew.build.version
            FROM brew.build
            LEFT JOIN brew.events ON brew.build.create_event = brew.events.id
            LEFT JOIN brew.package ON brew.build.pkg_id = brew.package.id
            LEFT JOIN brew.users ON brew.build.owner = brew.users.id
            WHERE brew.events.time IS NOT NULL AND brew.events.time >= '{0}'
                AND brew.events.time <= '{1}'
            ORDER BY brew.build.start_time DESC;
            """.format(start_date, end_date)

        return self.teiid.query(sql=sql_query)

    def get_task(self, task_id):
        """
        Query Teiid for a Koji task.

        :param int task_id: the Koji task ID to query
        :return: a list of dictionaries
        :rtype: list
        """
        # SQL query to fetch task related to a certain build
        sql_query = """
            SELECT arch, completion_time, create_time, id, "method", priority, request, start_time,
                   state, weight
            FROM brew.task
            WHERE id = {};
            """.format(task_id)

        return self.teiid.query(sql=sql_query)

    def get_build_tags(self, build_id):
        """
        Query Teiid for all tags a build is tagged in.

        :param int build_id: the Koji build's ID
        :return: a list of dictionaries
        :rtype: list
        """
        # SQL query to fetch tag name related to a certain build
        sql_query = """
            SELECT tag_listing.tag_id AS tag_id, tags.name AS tag_name
            FROM brew.tag_listing AS tag_listing
            LEFT JOIN brew.tag AS tags ON tag_listing.tag_id = tags.id
            WHERE tag_listing.active = True AND tag_listing.build_id = {};
            """.format(build_id)

        return self.teiid.query(sql=sql_query)

    def get_tag_info(self, tag_name):
        """
        Query Teiid for tag_id of a tag and build_ids associated to it.

        :param str tag_name: tag name
        :return: a list of dictionaries
        :rtype: list
        """
        sql_query = """
            SELECT tags.id AS tag_id, tag_listing.build_id
            FROM brew.tag_listing AS tag_listing
            LEFT JOIN brew.tag AS tags ON tag_listing.tag_id = tags.id
            WHERE tag_listing.active = True AND tags.name = '{}';
            """.format(tag_name)

        return self.teiid.query(sql=sql_query)

    def get_build_info(self, build_ids):
        """
        Query Teiid for build info.

        :param list build_ids: ID's of Koji builds
        :return: a list of dictionaries
        :rtype: list
        """
        if not build_ids:
            return []

        sql_query = """
                SELECT
                brew.events.time as creation_time,
                brew.build.completion_time,
                brew.build.epoch,
                brew.build.extra,
                brew.build.id,
                brew.users.name as owner_name,
                brew.package.name as package_name,
                brew.build.release,
                brew.build.start_time,
                brew.build.state,
                brew.build.task_id,
                brew.build.version
            FROM brew.build
            LEFT JOIN brew.events ON brew.build.create_event = brew.events.id
            LEFT JOIN brew.package ON brew.build.pkg_id = brew.package.id
            LEFT JOIN brew.users ON build.owner = brew.users.id
        """

        sql_query += 'WHERE build.id = ' + ' OR build.id = '.join(
            [str(build_id) for build_id in build_ids])

        return self.teiid.query(sql=sql_query)

    def update_neo4j(self, builds):
        """
        Update Neo4j with Koji build information from Teiid.

        :param list builds: a list of dictionaries
        """
        # Uploads builds data to their respective nodes
        log.info('Beginning to upload data to Neo4j')
        count = 0

        for build_dict in builds:
            build_params = dict(
                id_=build_dict['id'],
                epoch=build_dict['epoch'],
                state=build_dict['state'],
                creation_time=build_dict['creation_time'],
                start_time=build_dict['start_time'],
                completion_time=build_dict['completion_time'],
                extra=build_dict['extra'],
                name=build_dict['package_name'],
                version=build_dict['version'],
                release=build_dict['release']
            )

            try:
                extra_json = json.loads(build_dict['extra'])
            except (ValueError, TypeError):
                extra_json = {}

            if self.is_container_build(build_dict):
                build_params['operator'] = bool(
                    extra_json.get('typeinfo', {}).get('operator-manifests', {}).get('archive')
                )
                try:
                    build = ContainerKojiBuild.create_or_update(build_params)[0]
                except neomodel.exceptions.ConstraintValidationFailed:
                    # This must have errantly been created as a KojiBuild instead of a
                    # ContainerKojiBuild, so let's fix that.
                    build = KojiBuild.nodes.get_or_none(id_=build_params['id_'])
                    if not build:
                        # If there was a constraint validation failure and the build isn't just the
                        # wrong label, then we can't recover.
                        raise
                    build.add_label(ContainerKojiBuild.__label__)
                    build = ContainerKojiBuild.create_or_update(build_params)[0]
            elif self.is_module_build(build_dict):
                module_extra_info = extra_json.get('typeinfo', {}).get('module')
                try:
                    build_params['context'] = module_extra_info.get('context')
                    build_params['mbs_id'] = module_extra_info.get('module_build_service_id')
                    build_params['module_name'] = module_extra_info.get('name')
                    build_params['module_stream'] = module_extra_info.get('stream')
                    build_params['module_version'] = module_extra_info.get('version')
                    build = ModuleKojiBuild.create_or_update(build_params)[0]
                except neomodel.exceptions.ConstraintValidationFailed:
                    # This must have errantly been created as a KojiBuild instead of a
                    # ModuleKojiBuild, so let's fix that.
                    build = KojiBuild.nodes.get_or_none(id_=build_params['id_'])
                    if not build:
                        # If there was a constraint validation failure and the build isn't just the
                        # wrong label, then we can't recover.
                        raise
                    build.add_label(ModuleKojiBuild.__label__)
                    build = ModuleKojiBuild.create_or_update(build_params)[0]
            else:
                build = KojiBuild.create_or_update(build_params)[0]

            username = build_dict['owner_name']
            user = User.get_or_create(dict(username=username))[0]
            build.conditional_connect(build.owner, user)

            if build.__label__ == ModuleKojiBuild.__label__:
                module_build_tag_name = module_extra_info.get('content_koji_tag')
                if module_build_tag_name:
                    module_components = self.get_tag_info(module_build_tag_name)
                    # Some modules don't have components
                    if module_components:
                        module_build_tag = KojiTag.create_or_update(dict(
                            id_=module_components[0]['tag_id'],
                            name=module_build_tag_name
                        ))[0]
                        module_build_tag.conditional_connect(module_build_tag.module_builds, build)

                        for item in module_components:
                            module_component = KojiBuild.get_or_create(dict(
                                id_=item['build_id']
                            ))[0]
                            build.components.connect(module_component)

                        component_builds = self.get_build_info(
                            [item['build_id'] for item in module_components])
                        self.update_neo4j(component_builds)

            tags = self.get_build_tags(build_dict['id'])
            current_tag_ids = set()
            for _tag in tags:
                current_tag_ids.add(_tag['tag_id'])
                tag = KojiTag.create_or_update(dict(
                    id_=_tag['tag_id'],
                    name=_tag['tag_name']
                ))[0]

                tag.builds.connect(build)

            # _tag.id_ must be cast as an int because it is stored as a string in Neo4j since
            # it's a UniqueIdProperty
            connected_tags = {int(_tag.id_): _tag for _tag in build.tags.all()}
            extra_connected_tag_ids = set(connected_tags.keys()) - current_tag_ids
            for tag_id in extra_connected_tag_ids:
                build.tags.disconnect(connected_tags[tag_id])

            count += 1
            log.info('Uploaded {0} builds out of {1}'.format(count, len(builds)))

            container_koji_task_id = extra_json.get('container_koji_task_id')
            if build_dict['task_id']:
                task_id = build_dict['task_id']
            elif container_koji_task_id:
                task_id = container_koji_task_id
            else:
                # Continue if the task_id is None
                continue
            # Getting task related to the current build
            try:
                task_dict = self.get_task(task_id)[0]
            except IndexError:
                continue

            commit_hash = None
            # Only look for the commit hash if the build is an RPM or container
            if task_dict['method'] in ('build', 'buildContainer'):
                xml_root = ET.fromstring(task_dict['request'])
                for child in xml_root.iter('string'):
                    if child.text and child.text.startswith('git'):
                        commit_hash = child.text.rsplit('#', 1)[1]
                        break

            if commit_hash:
                commit = DistGitCommit.get_or_create(dict(hash_=commit_hash))[0]
                build.conditional_connect(build.commit, commit)
