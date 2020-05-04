# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import xml.etree.ElementTree as ET

import neomodel
from requests.exceptions import ConnectionError

from scrapers.base import BaseScraper
from estuary.models.freshmaker import FreshmakerEvent, FreshmakerBuild
from estuary.models.errata import Advisory
from estuary.models.koji import ContainerKojiBuild, KojiBuild
from scrapers.utils import retry_session
from estuary import log
from estuary.utils.general import timestamp_to_datetime


class FreshmakerScraper(BaseScraper):
    """Scrapes the Freshmaker API."""

    freshmaker_url = "https://freshmaker.engineering.redhat.com/api/1/events/?per_page=50"

    def run(self, since=None, until=None):
        """
        Run the Freshmaker scraper.

        :param str since: a datetime to start scraping data from
        :param str until: a datetime to scrape data until
        """
        if since or until:
            log.warn('Ignoring the since/until parameter; They do not apply to the'
                     'Freshmaker scraper')
        log.info('Starting initial load of Freshmaker events')
        self.query_api_and_update_neo4j()
        log.info('Initial load of Freshmaker events complete!')

    def query_api_and_update_neo4j(self):
        """
        Scrape the Freshmaker API and upload the data to Neo4j.

        :param str start_date: a datetime to start scraping data from
        """
        # Initialize session and url
        session = retry_session()
        fm_url = self.freshmaker_url
        while True:
            log.debug('Querying {0}'.format(fm_url))
            try:
                rv_json = session.get(fm_url, timeout=60).json()
            except ConnectionError:
                # TODO: Remove this once FACTORY-3955 is resolved
                log.error(
                    'The connection to Freshmaker at %s failed. Skipping the rest of the scraper.',
                    fm_url,
                )
                break

            for fm_event in rv_json['items']:
                try:
                    int(fm_event['search_key'])
                except ValueError:
                    # Skip Freshmaker Events that don't have the search_key as the Advisory ID
                    continue
                if fm_event.get('dry_run'):
                    # Skip events triggered by manual rebuilds in dry run mode
                    continue
                log.debug('Creating FreshmakerEvent {0}'.format(fm_event['id']))
                event_params = dict(
                    id_=fm_event['id'],
                    state_name=fm_event['state_name'],
                    state_reason=fm_event['state_reason'],
                    url=fm_event['url']
                )
                if fm_event.get('time_created'):
                    event_params['time_created'] = timestamp_to_datetime(fm_event['time_created'])
                if fm_event.get('time_done'):
                    event_params['time_done'] = timestamp_to_datetime(fm_event['time_created'])
                event = FreshmakerEvent.create_or_update(event_params)[0]

                log.debug('Creating Advisory {0}'.format(fm_event['search_key']))
                advisory = Advisory.get_or_create(dict(
                    id_=fm_event['search_key']
                ))[0]

                event.conditional_connect(event.triggered_by_advisory, advisory)

                for build_dict in fm_event['builds']:
                    # To handle a faulty container build in Freshmaker
                    if build_dict['build_id'] and int(build_dict['build_id']) < 0:
                        continue
                    log.debug('Creating FreshmakerBuild {0}'.format(build_dict['build_id']))
                    fb_params = dict(
                        id_=build_dict['id'],
                        dep_on=build_dict['dep_on'],
                        name=build_dict['name'],
                        original_nvr=build_dict['original_nvr'],
                        rebuilt_nvr=build_dict['rebuilt_nvr'],
                        state_name=build_dict['state_name'],
                        state_reason=build_dict['state_reason'],
                        time_submitted=timestamp_to_datetime(build_dict['time_submitted']),
                        type_=build_dict['type'],
                        type_name=build_dict['type_name'],
                        url=build_dict['url']
                    )
                    if build_dict['time_completed']:
                        fb_params['time_completed'] = timestamp_to_datetime(
                            build_dict['time_completed'])
                    if build_dict['build_id']:
                        fb_params['build_id'] = build_dict['build_id']
                    fb = FreshmakerBuild.create_or_update(fb_params)[0]
                    event.requested_builds.connect(fb)

                    # The build ID obtained from Freshmaker API is actually a Koji task ID
                    task_result = None
                    if build_dict['build_id']:
                        task_result = self.get_koji_task_result(build_dict['build_id'])

                    if not task_result:
                        continue

                    # Extract the build ID from a task result
                    xml_root = ET.fromstring(task_result)
                    # TODO: Change this if a task can trigger multiple builds
                    try:
                        build_id = xml_root.find(".//*[name='koji_builds'].//string").text
                    except AttributeError:
                        build_id = None

                    if not build_id:
                        continue

                    log.debug('Creating ContainerKojiBuild {0}'.format(build_id))
                    build_params = {
                        'id_': build_id,
                        'original_nvr': build_dict['original_nvr']
                    }
                    try:
                        build = ContainerKojiBuild.create_or_update(build_params)[0]
                    except neomodel.exceptions.ConstraintValidationFailed:
                        # This must have errantly been created as a KojiBuild instead of a
                        # ContainerKojiBuild, so let's fix that.
                        build = KojiBuild.nodes.get_or_none(id_=build_id)
                        if not build:
                            # If there was a constraint validation failure and the build isn't just
                            # the wrong label, then we can't recover.
                            raise
                        build.add_label(ContainerKojiBuild.__label__)
                        build = ContainerKojiBuild.create_or_update(build_params)[0]

                    event.successful_koji_builds.connect(build)

            if rv_json['meta'].get('next'):
                fm_url = rv_json['meta']['next']
            else:
                break

    def get_koji_task_result(self, task_id):
        """
        Query Teiid for a Koji task's result attribute.

        :param int task_id: the Koji task ID to query
        :return: an XML string
        :rtype: str
        """
        # SQL query to fetch task related to a certain build
        sql_query = """
            SELECT result
            FROM brew.task
            WHERE id = {};
            """.format(task_id)

        try:
            return self.teiid.query(sql=sql_query)[0]['result']
        except (IndexError, KeyError):
            return None
