# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def retry_session():
    """
    Create a python-requests session that retries on connection failures.

    :return: a configured session object
    :rtype: requests.Session
    """
    session = requests.Session()
    retry = Retry(
        total=5,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        method_whitelist=('GET')
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
