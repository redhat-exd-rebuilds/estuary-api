# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from purview import version

import json


def test_about_endpoint(client):
    rv = client.get('/api/v1/about')
    assert json.loads(rv.data.decode('utf-8')) == {'version': version}
