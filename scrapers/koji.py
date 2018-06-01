# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import xml.etree.ElementTree as ET
import json

from scrapers.base import BaseScraper
from purview.models.koji import KojiBuild, KojiTask, KojiTag
from purview.models.user import User
from purview.models.distgit import DistGitCommit
import purview.utils.general as utils
from purview import log


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
            since = self.default_since
        else:
            since = utils.timestamp_to_datetime(since)

        if until is None:
            until = self.default_until
        else:
            until = utils.timestamp_to_datetime(until)
        builds = self.get_koji_builds(since, until)
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
        log.info('Getting all Koji builds since {0}'.format(start_date))
        sql_query = """
            SELECT
                events.time as creation_time,
                build.completion_time,
                build.epoch,
                build.extra,
                build.id,
                brew.users.name as owner_name,
                brew.users.krb_principal as owner_username,
                package.name as package_name,
                build.release,
                build.start_time,
                build.state,
                build.task_id,
                build.version
            FROM build
            LEFT JOIN events ON build.create_event = events.id
            LEFT JOIN package ON build.pkg_id = package.id
            LEFT JOIN brew.users ON build.owner = brew.users.id
            WHERE events.time IS NOT NULL AND events.time >= '{0}' AND events.time <= '{1}'
            ORDER BY build.id
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
            WHERE id = {}
            """.format(task_id)

        return self.teiid.query(sql=sql_query)

    def get_task_children(self, parent):
        """
        Query Teiid for all child tasks of a Koji task.

        :param int parent: the parent Koji task ID
        :return: a list of dictionaries
        :rtype: list
        """
        # SQL query to fetch all child tasks related to a
        # parent task
        sql_query = """
            SELECT arch, completion_time, create_time, id, "method", priority, request, start_time,
                   state, weight
            FROM brew.task
            WHERE parent = {}
            """.format(parent)

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
            WHERE tag_listing.active = True AND tag_listing.build_id = {}
            """.format(build_id)

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
            build = KojiBuild.create_or_update(dict(
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
            ))[0]

            if build_dict['owner_username']:
                username = build_dict['owner_username'].split('@')[0]
            else:
                username = build_dict['owner_name']
            user = User.get_or_create(dict(username=username))[0]
            build.conditional_connect(build.owner, user)

            tags = self.get_build_tags(build_dict['id'])
            current_tag_ids = set()
            for _tag in tags:
                current_tag_ids.add(_tag['tag_id'])
                tag = KojiTag.get_or_create(dict(
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

            try:
                extra_json = json.loads(build_dict['extra'])
            except (json.JSONDecodeError, TypeError):
                extra_json = {}

            container_koji_task_id = extra_json.get('container_koji_task_id')
            if build_dict['task_id']:
                task_id = build_dict['task_id']
            elif container_koji_task_id:
                task_id = container_koji_task_id
            else:
                # Continue if the task_id is None
                continue
            # Getting task related to the current build
            task_dict = self.get_task(task_id)[0]
            xml_root = ET.fromstring(task_dict['request'])
            commit_hash = None
            for child in xml_root.iter('string'):
                if child.text and child.text.startswith('git'):
                    commit_hash = child.text.rsplit('#', 1)[1]
                    break

            if not task_dict:
                # Continue if no corresponding task found
                continue

            task = KojiTask.create_or_update(dict(
                id_=task_dict['id'],
                weight=task_dict['weight'],
                create_time=task_dict['create_time'],
                start_time=task_dict['start_time'],
                completion_time=task_dict['completion_time'],
                state=task_dict['state'],
                priority=task_dict['priority'],
                arch=task_dict['arch'],
                method=task_dict['method']
            ))[0]

            # Defining Relationships
            task.builds.connect(build)
            task.conditional_connect(task.owner, user)
            if commit_hash:
                commit = DistGitCommit.get_or_create(dict(hash_=commit_hash))[0]
                build.conditional_connect(build.commit, commit)

            child_tasks = self.get_task_children(task_dict['id'])

            if not child_tasks:
                # Continue if no corresponding child task found
                continue

            for child_task_dict in child_tasks:
                child_task = KojiTask.create_or_update(dict(
                    id_=child_task_dict['id'],
                    weight=child_task_dict['weight'],
                    create_time=child_task_dict['create_time'],
                    start_time=child_task_dict['start_time'],
                    completion_time=child_task_dict['completion_time'],
                    state=child_task_dict['state'],
                    priority=child_task_dict['priority'],
                    arch=child_task_dict['arch'],
                    method=child_task_dict['method']
                ))[0]
                child_task.conditional_connect(child_task.parent, task)
