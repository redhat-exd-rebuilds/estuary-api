# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import mock
import pytest

from estuary.models.koji import KojiBuild
from estuary.app import create_app
from estuary.auth import EstuaryOIDC


@mock.patch('estuary.auth.EstuaryOIDC', autospec=True)
def test_get_story_auth_no_header(mock_oidc):
    """Test accessing a protected route without the "Authorization" header."""
    client = create_app('estuary.config.TestAuthConfig').test_client()
    mock_oidc.assert_called_once()
    rv = client.get('/api/v1/story/kojibuild/2345')
    expected = {
        'message': 'An "Authorization" header wasn\'t provided',
        'status': 401
    }
    assert rv.status_code == 401
    assert json.loads(rv.data.decode('utf-8')) == expected


@mock.patch('estuary.auth.EstuaryOIDC', autospec=True)
def test_get_story_auth_invalid_header(mock_oidc):
    """Test accessing a protected route with an invalid "Authorization" header."""
    client = create_app('estuary.config.TestAuthConfig').test_client()
    mock_oidc.assert_called_once()
    rv = client.get('/api/v1/story/kojibuild/2345', headers={'Authorization': 'not bearer'})
    expected = {
        'message': 'The "Authorization" header must start with "Bearer"',
        'status': 401
    }
    assert rv.status_code == 401
    assert json.loads(rv.data.decode('utf-8')) == expected


@mock.patch('estuary.auth.EstuaryOIDC', autospec=True)
def test_get_story_auth_invalid_token(mock_oidc):
    """Test accessing a protected route with an invalid token."""
    mock_oidc.return_value.validate_token.return_value = 'Token required but invalid'
    client = create_app('estuary.config.TestAuthConfig').test_client()
    mock_oidc.assert_called_once()
    rv = client.get('/api/v1/story/kojibuild/2345', headers={'Authorization': 'Bearer 123456'})
    expected = {
        'message': 'Token required but invalid',
        'status': 401
    }
    assert rv.status_code == 401
    assert json.loads(rv.data.decode('utf-8')) == expected


@mock.patch('estuary.auth.EstuaryOIDC', autospec=True)
def test_get_story_auth_not_employee(mock_oidc):
    """Test accessing a protected route with a valid token of a non-employee."""
    mock_oidc.return_value.validate_token.return_value = True
    mock_oidc.return_value._get_token_info.return_value = \
        {'active': True, 'employeeType': 'Contractor'}
    client = create_app('estuary.config.TestAuthConfig').test_client()
    mock_oidc.assert_called_once()
    rv = client.get('/api/v1/story/kojibuild/2345', headers={'Authorization': 'Bearer 123456'})
    expected = {
        'message': 'You must be an employee to access this service',
        'status': 401
    }
    assert rv.status_code == 401
    assert json.loads(rv.data.decode('utf-8')) == expected


@pytest.mark.parametrize('employee_type', ('Employee', 'International Local Hire'))
@mock.patch('estuary.auth.EstuaryOIDC', autospec=True)
def test_get_story_auth(mock_oidc, employee_type):
    """Test getting the story when authentication is required."""
    mock_oidc.return_value.validate_token.return_value = True
    mock_oidc.return_value._get_token_info.return_value = \
        {'active': True, 'employeeType': employee_type}
    client = create_app('estuary.config.TestAuthConfig').test_client()
    mock_oidc.assert_called_once()

    KojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '2345',
        'name': 'slf4j',
        'release': '4.el7_4',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.4'
    })[0]

    expected = {
        'data': [
            {
                'advisories': [],
                'commit': None,
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'id': '2345',
                'name': 'slf4j',
                'owner': None,
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'module_builds': [],
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'tags': [],
                'timeline_timestamp': '2017-04-02T19:39:06Z',
                'version': '1.7.4'
            }
        ],
        'meta': {
            'requested_node_index': 0,
            'story_related_nodes_backward': [0],
            'story_related_nodes_forward': [0],
            'story_type': 'container',
            'total_lead_time': 0.0,
            'total_processing_time': 0.0,
            'processing_time_flag': False,
            'total_wait_time': 0.0,
            'wait_times': [0]
        }
    }

    rv = client.get('/api/v1/story/kojibuild/2345', headers={'Authorization': 'Bearer 123456'})
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_load_secrets():
    """Test that EstuaryOIDC.load_secrets returns the correct dictionary."""
    app = create_app('estuary.config.TestAuthConfig')
    oidc = EstuaryOIDC()
    assert oidc.load_secrets(app) == {
        'web': {
            'redirect_uris': None,
            'token_uri': None,
            'auth_uri': None,
            'client_id': 'estuary',
            'client_secret': 'some_secret',
            'userinfo_uri': None,
            'token_introspection_uri': 'https://provider.domain.local/oauth2/default/v1/introspect'
        }
    }
