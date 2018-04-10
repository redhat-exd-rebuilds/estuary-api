# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from mock import patch

from purview import version
from purview.models.user import User

import json


def test_about_endpoint(client):
    rv = client.get('/api/v1/about')
    assert json.loads(rv.data.decode('utf-8')) == {'version': version}


def test_get_user(client):
    user = User(id=71, username='someuser', email='someuser@redhat.com')
    with patch('neomodel.match.NodeSet.get_or_none') as mock_neo4j:
        mock_neo4j.return_value = user
        rv = client.get('/api/v1/user/someuser')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == user.serialized
