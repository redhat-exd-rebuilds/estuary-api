# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime, date, timedelta

from neomodel import config as neomodel_config

from scrapers.teiid import Teiid


class BaseScraper(object):
    """Base scraper class to standardize the main scraper functionality."""

    teiid_host = 'virtualdb.engineering.redhat.com'
    teiid_port = 5432
    # Default start date and end date to fetch data
    default_since = (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d')
    default_until = str(date.today())

    def __init__(self, teiid_user=None, teiid_password=None, kerberos=False, neo4j_user='neo4j',
                 neo4j_password='neo4j', neo4j_server='localhost'):
        """
        Initialize the BaseScraper class.

        :kwarg str teiid_user: the user to connect as
        :kwarg str teiid_password: the password to connect as
        :kwarg bool kerberos: if Kerberos authentication should be used
        :kwarg str neo4j_user: the Neo4j user to connect as
        :kwarg str neo4j_password: the Neo4j user's password to connect with
        :kwarg str neo4j_server: the FQDN of the Neo4j server
        """
        if kerberos:
            # In case credentials were passed in, we can wipe them since we won't be using them
            teiid_user = None
            teiid_password = None
            self.teiid_port = 5433
        self.teiid = Teiid(self.teiid_host, self.teiid_port, teiid_user, teiid_password)
        neomodel_config.DATABASE_URL = 'bolt://{user}:{password}@{server}:7687'.format(
            user=neo4j_user, password=neo4j_password, server=neo4j_server)

    def run(self, since=None):
        """
        Run the scraper.

        :kwarg str since: a datetime to start scraping data from
        :raises NotImplementedError: if the function is not overridden
        """
        raise NotImplementedError()
