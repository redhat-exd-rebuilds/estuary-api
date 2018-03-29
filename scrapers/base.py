# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

from neomodel import config as neomodel_config

from purview.utils.teiid import Teiid


class BaseScraper(object):
    """
    Base scraper class to standardize the main scraper functionality
    """
    teiid_host = 'virtualdb.engineering.redhat.com'
    teiid_port = 5432

    def __init__(self, teiid_user=None, teiid_password=None, kerberos=False, neo4j_user='neo4j',
                 neo4j_password='neo4j', neo4j_server='localhost'):
        """
        Initializes the BaseScraper class
        :kwarg teiid_user: a string of the user to connect as
        :kwarg teiid_password: a string of the password to connect as
        :kwarg kerberos: a bool determining if Kerberos authentication should be used
        :kwarg neo4j_user: a string of the Neo4j user to connect as
        :kwarg neo4j_password: a string of the Neo4j user's password to connect with
        :kwarg neo4j_server: a string of the FQDN of the Neo4j server
        :return: None
        """
        if kerberos:
            # In case credentials were passed in, we can wipe them since we won't be using them
            teiid_user = None
            teiid_password = None
            self.teiid_port = 5433
            # Default start date to fetch data from
            self.default_since = datetime(2016, 3, 1)
        self.teiid = Teiid(self.teiid_host, self.teiid_port, teiid_user, teiid_password)
        neomodel_config.DATABASE_URL = 'bolt://{user}:{password}@{server}:7687'.format(
            user=neo4j_user, password=neo4j_password, server=neo4j_server)

    def run(self, since=None):
        """
        Run the scraper
        :kwarg since: a string of a UTC timestamp in the ISO 8601 format or
        a datetime object
        :return: None
        """
        raise NotImplementedError()
