# SPDX-License-Identifier: GPL-3.0+
from scrapers.base import BaseScraper
from purview.models.koji import KojiBuild, KojiTask
from purview.models.user import User
import purview.utils.general as utils

import logging

log = logging.getLogger(__name__)


class KojiScraper(BaseScraper):

    def run(self, since=None):
        log.info('Starting initial load for Koji')
        # Initialize a start date from which all builds must be fetched
        # If no input is given by the user, fetch builds from the past two years
        if since is None:
            since = self.default_since
        else:
            since = utils.timestamp_to_datetime(since)

        self.builds = self.get_koji_builds(since)
        self.update_neo4j(self.builds)
        log.info('Initial load of Koji builds complete!')

    def get_koji_builds(self, start_date):
        # SQL query to fetch all builds from start date until now
        log.info('Getting all Koji builds since {0}'.format(start_date))
        sql_query = """
            SELECT build.*, events.time as creation_time, package.name as package_name
            FROM build
            LEFT JOIN events ON build.create_event = events.id
            LEFT JOIN package ON build.pkg_id = package.id
            WHERE events.time IS NOT NULL AND events.time >= '{}'
            """.format(start_date)

        log.debug("Query:", sql_query.strip())
        builds = self.teiid.query(sql=sql_query, retry=3)
        log.info('Successfully fetched {0} builds from teiid'.format(len(builds)))
        return builds

    def get_task(self, task_id):
        # SQL query to fetch task related to a certain build
        sql_query = """
            SELECT *
            FROM brew.task
            WHERE id = {}
            """.format(task_id)

        self.task = self.teiid.query(sql=sql_query, retry=3)
        return self.task

    def get_task_children(self, parent):
        # SQL query to fetch all child tasks related to a
        # parent task
        sql_query = """
            SELECT *
            FROM brew.task
            WHERE parent = {}
            """.format(parent)

        self.task = self.teiid.query(sql=sql_query, retry=3)
        return self.task

    def update_neo4j(self, builds):
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

            user = User.get_or_create(dict(
                username=build_dict['owner']
            ))[0]

            build.owner.connect(user)
            user.koji_builds.connect(build)

            count += 1
            log.info('Uploaded {0} builds out of {1}'.format(count, len(builds)))

            if build_dict['task_id']:
                # Getting task related to the current build
                task_dict = self.get_task(build_dict['task_id'])[0]
            else:
                # Continue if the task_id is None
                continue

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
            build.tasks.connect(task)
            user.koji_tasks.connect(task)
            task.builds.connect(build)
            task.owner.connect(user)

            if task_dict['parent']:
                # Getting child tasks of a parent task
                child_tasks = self.get_task_children(task_dict['parent'])
            else:
                # Continue if the parent is None
                continue

            if not child_tasks:
                # Continue if no corresponding child task found
                continue

            for child_task_dict in child_tasks:
                child_task = KojiTask.create_or_update(dict(
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

            child_task.parents.connect(task)
            task.children.connect(child_task)
