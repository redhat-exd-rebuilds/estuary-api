# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from purview import version
from purview.models.user import User

import json


def test_about_endpoint(client):
    rv = client.get('/api/v1/about')
    assert json.loads(rv.data.decode('utf-8')) == {'version': version}


def test_get_user(client):
    # Create a placeholder user
    user = User.get_or_create({'username': 'tbrady', 'email': 'tom.brady@domain.local'})[0]
    rv = client.get('/api/v1/user/tbrady')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == user.serialized
