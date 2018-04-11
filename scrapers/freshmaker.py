# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from scrapers.base import BaseScraper
from purview.models.freshmaker import FreshmakerEvent, ContainerBuilds
from purview.models.errata import Advisory
from scrapers.utils import retry_session
from purview.utils.general import timestamp_to_datetime
from purview import log


class FreshmakerScraper(BaseScraper):
    # Defining URL for Freshmaker API
    freshmaker_url = "https://freshmaker.engineering.redhat.com/api/1/events/?per_page=100"

    def run(self, since=None):
        """
        Main function that runs the Freshmaker scraper
        :param since: a string representing a datetime to start scraping data from
        :return: None
        """
        if since:
            log.warn('Ignoring the since parameter; It doesn\'t apply to the Freshmaker scraper')
        log.info('Starting initial load of Freshmaker events')
        self.query_api_and_update_neo4j()
        log.info('Initial load of Freshmaker events complete!')

    def query_api_and_update_neo4j(self):
        """
        Scrapes Freshmaker API and uploads data to Neo4j
        :param start_date: a string representing a datetime to start scraping data from
        :return: None
        """
        # Initialize session and url
        session = retry_session()
        fm_url = self.freshmaker_url
        while True:
            log.debug('Querying {0}'.format(fm_url))
            rv_json = session.get(fm_url, timeout=15).json()
            for fm_event in rv_json['items']:
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

                advisory.triggers_freshmaker_event.connect(event)
                event.triggered_by_advisory.connect(advisory)

                for build in fm_event['builds']:
                    # To handle a faulty container build in Freshmaker
                    if not build['build_id']:
                        continue

                    cb_params = dict(
                        id_=build['id'],
                        build_id=build['build_id'],
                        dep_on=build['dep_on'],
                        event_id=build['event_id'],
                        name=build['name'],
                        original_nvr=build['original_nvr'],
                        rebuilt_nvr=build['rebuilt_nvr'],
                        state=build['state'],
                        state_name=build['state_name'],
                        state_reason=build['state_reason'],
                        time_submitted=timestamp_to_datetime(build['time_submitted']),
                        type_=build['type'],
                        type_name=build['type_name'],
                        url=build['url']
                    )
                    if build['time_completed']:
                        cb_params['time_completed'] = timestamp_to_datetime(
                            build['time_completed'])
                    cb = ContainerBuilds.create_or_update(cb_params)[0]
                    cb.triggered_by_freshmaker_event.connect(event)
                    event.triggers_container_builds.connect(cb)

            if rv_json['meta'].get('next'):
                fm_url = rv_json['meta']['next']
            else:
                break
