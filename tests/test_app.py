# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


def test_insert_headers(client):
    """Test that the appropriate headers are inserted in a Flask response."""
    rv = client.get('/api/v1/')
    assert 'Access-Control-Allow-Origin: *' in str(rv.headers)
    assert 'Access-Control-Allow-Headers: Content-Type' in str(rv.headers)
    assert 'Access-Control-Allow-Method: GET, OPTIONS' in str(rv.headers)
