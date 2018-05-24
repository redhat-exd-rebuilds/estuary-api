# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import xml.etree.ElementTree as ET

from scrapers.base import BaseScraper
from purview.models.freshmaker import FreshmakerEvent
from purview.models.errata import Advisory
from purview.models.koji import KojiBuild
from scrapers.utils import retry_session
from purview import log


class FreshmakerScraper(BaseScraper):
    """Scrapes the Freshmaker API."""

    freshmaker_url = "https://freshmaker.engineering.redhat.com/api/1/events/?per_page=100"

    def run(self, since=None):
        """
        Run the Freshmaker scraper.

        :param str since: a datetime to start scraping data from
        """
        if since:
            log.warn('Ignoring the since parameter; It doesn\'t apply to the Freshmaker scraper')
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
            rv_json = session.get(fm_url, timeout=15).json()
            for fm_event in rv_json['items']:
                try:
                    int(fm_event['search_key'])
                except ValueError:
                    # Skip Freshmaker Events that don't have the search_key as the Advisory ID
                    continue
                event = FreshmakerEvent.create_or_update(dict(
                    id_=fm_event['id'],
                    event_type_id=fm_event['event_type_id'],
                    message_id=fm_event['message_id'],
                    state=fm_event['state'],
                    state_name=fm_event['state_name'],
                    state_reason=fm_event['state_reason'],
                    url=fm_event['url']
                ))[0]

                advisory = Advisory.get_or_create(dict(
                    id_=fm_event['search_key']
                ))[0]

                event.conditional_connect(event.triggered_by_advisory, advisory)

                for build_dict in fm_event['builds']:
                    # To handle a faulty container build in Freshmaker
                    if not build_dict['build_id'] or int(build_dict['build_id']) < 0:
                        continue

                    try:
                        # The build ID obtained from Freshmaker API is actually a Koji task ID
                        task_result = self.get_task_results(build_dict['build_id'])[0]
                    except IndexError:
                        continue

                    # Extract the build ID from a task result
                    xml_root = ET.fromstring(task_result['result'])
                    # TODO: Change this if a task can trigger multiple builds
                    build_id = xml_root.find(".//*[name='koji_builds'].//string")

                    if build_id:
                        build = KojiBuild.get_or_create(dict(id_=build_id))[0]
                        event.triggered_container_builds.connect(build)

            if rv_json['meta'].get('next'):
                fm_url = rv_json['meta']['next']
            else:
                break

    def get_task_results(self, task_id):
        """
        Query Teiid for a Koji task's result attribute.

        :param int task_id: the Koji task ID to query
        :return: a list of dictionaries
        :rtype: list
        """
        # SQL query to fetch task related to a certain build
        sql_query = """
            SELECT result
            FROM brew.task
            WHERE id = {}
            """.format(task_id)

        return self.teiid.query(sql=sql_query)
