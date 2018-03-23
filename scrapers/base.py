# SPDX-License-Identifier: GPL-3.0+

from purview.utils.teiid import Teiid
from datetime import datetime


class BaseScraper(object):
    """
    Base scraper class to standardize the main scraper functionality
    """
    teiid_host = 'virtualdb.engineering.redhat.com'
    teiid_port = 5432

    def __init__(self, teiid_user=None, teiid_password=None, kerberos=False):
        """
        Initializes the BaseScraper class
        :kwarg teiid_user: a string of the user to connect as
        :kwarg teiid_password: a string of the password to connect as
        :kwarg kerberos: a bool determining if Kerberos authentication should be used
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

    def run(self, since=None):
        """
        Run the scraper
        :kwarg since: a string of a UTC timestamp in the ISO 8601 format or
        a datetime object
        :return: None
        """
        raise NotImplementedError()
