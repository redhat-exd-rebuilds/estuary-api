# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('origin, header_set', [
    ('http://localhost:4200', True),
    ('http://some-hacker.domain.local', False)
])
def test_cors_header(client, origin, header_set):
    """Test that the appropriate headers are inserted in a Flask response."""
    rv = client.get('/api/v1/', headers={'Origin': origin})
    if header_set:
        assert 'Access-Control-Allow-Origin: {}'.format(origin) in str(rv.headers)
        assert 'Access-Control-Allow-Headers: Content-Type' in str(rv.headers)
        assert 'Access-Control-Allow-Method: GET, OPTIONS' in str(rv.headers)
    else:
        assert 'Access-Control-Allow-Origin' not in str(rv.headers)
        assert 'Access-Control-Allow-Headers' not in str(rv.headers)
        assert 'Access-Control-Allow-Method' not in str(rv.headers)
