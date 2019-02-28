# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from mock import patch


def test_healthcheck(client):
    """Test the health check endpoint is working."""
    rv = client.get('/healthcheck')
    assert rv.status_code == 200
    assert rv.data.decode('utf-8') == 'Health check OK'


def test_healthcheck_failure(client):
    """Test the health check endpoint shows failures."""
    with patch('estuary.api.health_check.db') as mock_db:
        mock_db.cypher_query.side_effect = RuntimeError('Some failure')
        rv = client.get('/healthcheck')
    assert rv.status_code == 503
    assert rv.data.decode('utf-8') == \
        'The health check failed while verifying the database connection'
