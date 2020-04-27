# SPDX-License-Identifier: GPL-3.0+
from __future__ import unicode_literals
from builtins import bytes

from scrapers.base import BaseScraper
from estuary.models.bugzilla import BugzillaBug
from estuary.models.user import User
from estuary.utils.general import timestamp_to_date
from estuary import log


class BugzillaScraper(BaseScraper):
    """Scrapes the Bugzilla tables in Teiid."""

    def run(self, since=None, until=None):
        """
        Run the Bugzilla scraper.

        :param str since: a datetime to start scraping data from
        :param str until: a datetime to scrape data until
        """
        log.info('Starting initial load of Bugzilla bugs')
        if since is None:
            start_date = self.default_since
        else:
            start_date = timestamp_to_date(since)
        if until is None:
            end_date = self.default_until
        else:
            end_date = timestamp_to_date(until)

        bugs = self.get_bugzilla_bugs(start_date, end_date)
        log.info('Successfully fetched {0} bugs from teiid'.format(len(bugs)))
        self.update_neo4j(bugs)
        log.info('Initial load of Bugzilla bugs complete!')

    def get_bugzilla_bugs(self, start_date, end_date):
        """
        Get the Buzilla bugs information from Teiid.

        :param datetime.datetime start_date: when to start scraping data from
        :param datetime.datetime end_date: determines until when to scrape data
        :return: list of dictionaries containing bug info
        :rtype: list
        """
        log.info('Getting all Bugzilla bugs since {0} until {1}'.format(start_date, end_date))
        sql_query = """
            SELECT bugs.*, products.name AS product_name, classifications.name AS classification,
                assigned.login_name AS assigned_to_email, reported.login_name AS reported_by_email,
                qa.login_name AS qa_contact_email
            FROM bugzilla.bugs AS bugs
            LEFT JOIN bugzilla.products AS products ON bugs.product_id = products.id
            LEFT JOIN bugzilla.classifications AS classifications
                ON products.classification_id = classifications.id
            LEFT JOIN bugzilla.profiles AS assigned ON bugs.assigned_to = assigned.userid
            LEFT JOIN bugzilla.profiles AS reported ON bugs.reporter = reported.userid
            LEFT JOIN bugzilla.profiles AS qa ON bugs.qa_contact = qa.userid
            WHERE classifications.name = 'Red Hat' AND bugs.delta_ts >= '{0}'
                AND bugs.delta_ts <= '{1}'
            ORDER BY bugs.creation_ts DESC;
            """.format(start_date, end_date)

        return self.teiid.query(sql=sql_query)

    def create_user_node(self, email):
        """
        Create a User node in Neo4j.

        :param str email: the user's email
        :return: User object
        """
        # If email is a Red Hat email address, username is same as domain name
        # prefix in the email address else store email as username
        if email.split('@')[1] == 'redhat.com':
            username = email.split('@')[0]
        else:
            username = email

        user = User.create_or_update(dict(
            username=username,
            email=email
        ))[0]
        return user

    def update_neo4j(self, bugs):
        """
        Update Neo4j with Bugzilla bugs information from Teiid.

        :param list bugs: a list of dictionaries
        """
        log.info('Beginning to upload data to Neo4j')
        count = 0

        for bug_dict in bugs:
            bug = BugzillaBug.create_or_update(dict(
                id_=bug_dict['bug_id'],
                severity=bug_dict['bug_severity'],
                status=bug_dict['bug_status'],
                creation_time=bug_dict['creation_ts'],
                modified_time=bug_dict['delta_ts'],
                priority=bug_dict['priority'],
                product_name=bytes(bug_dict['product_name'], 'utf-8').decode(),
                product_version=bug_dict['version'],
                classification=bug_dict['classification'],
                resolution=bug_dict['resolution'],
                target_milestone=bug_dict['target_milestone'],
                short_description=bytes(bug_dict['short_desc'], 'utf-8').decode()
            ))[0]

            count += 1
            log.info('Uploaded {0} bugs out of {1}'.format(count, len(bugs)))

            # Creating User nodes and updating their relationships
            if bug_dict['assigned_to']:
                assignee = self.create_user_node(bug_dict['assigned_to_email'])
                bug.conditional_connect(bug.assignee, assignee)

            if bug_dict['reporter']:
                reporter = self.create_user_node(bug_dict['reported_by_email'])
                bug.conditional_connect(bug.reporter, reporter)

            if bug_dict['qa_contact']:
                qa_contact = self.create_user_node(bug_dict['qa_contact_email'])
                bug.conditional_connect(bug.qa_contact, qa_contact)
