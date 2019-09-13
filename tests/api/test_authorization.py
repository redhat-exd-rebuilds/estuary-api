# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import ldap3
from mock import Mock, patch
import pytest
from werkzeug.exceptions import InternalServerError

from estuary.app import create_app
from estuary.authorization import is_user_authorized, _get_exception_users


@pytest.mark.parametrize('employeeType, authorized', (
    ('Employee', True),
    ('Contractor', False),
))
def test_is_user_authorized_with_employee(employeeType, authorized):
    """Test that only employees are authorized."""
    app = create_app('estuary.config.TestAuthConfig')
    with app.app_context():
        assert is_user_authorized('jlennon', employeeType) is authorized


@pytest.mark.parametrize('users, authorized', (
    ({'jlennon', 'pmccartney'}, True),
    ({'pmccartney'}, False),
))
@patch('estuary.authorization._get_exception_users')
def test_is_user_authorized_exception(mock_geu, users, authorized):
    """Test that a non-employee that is in the exceptions users is authorized."""
    mock_geu.return_value = users
    app = create_app('estuary.config.TestAuthConfig')
    app.config['LDAP_EXCEPTIONS_GROUP_DN'] = 'cn=something,dc=domain,dc=local'
    with app.app_context():
        assert is_user_authorized('jlennon', 'Contractor') is authorized


@pytest.mark.parametrize('ldap_uri', ('ldaps://domain.local', 'ldap://domain.local'))
def test_get_exception_users(ldap_uri):
    """Test that the exceptions list can be retrieved from LDAP."""
    app = create_app('estuary.config.TestAuthConfig')
    app.config['LDAP_URI'] = ldap_uri
    app.config['LDAP_EXCEPTIONS_GROUP_DN'] = 'cn=estuary-exceptions,cn=something,dc=domain,dc=local'
    # Create the mock LDAP instance
    server = ldap3.Server('ldaps://test.domain.local')
    connection = ldap3.Connection(server, client_strategy=ldap3.MOCK_SYNC)
    estuary_exceptions_group_attrs = {
        app.config['LDAP_GROUP_MEMBERSHIP_ATTRIBUTE']: [
            'uid=mprahl,ou=users,dc=domain,dc=local',
            'uid=tbrady,ou=users,dc=domain,dc=local',
        ],
        'cn': ['estuary-exceptions'],
        'gidNumber': 1234,
        'objectClass': ['top', 'groupOfUniqueNames', 'rhatRoverGroup'],
    }
    connection.strategy.add_entry(
        app.config['LDAP_EXCEPTIONS_GROUP_DN'],
        estuary_exceptions_group_attrs,
    )

    with app.app_context():
        with patch.object(ldap3, 'Tls', Mock(wraps=ldap3.Tls)) as mock_ldap_tls:
            with patch('ldap3.Connection') as mock_ldap:
                mock_ldap.return_value = connection
                assert _get_exception_users() == {'mprahl', 'tbrady'}

            if ldap_uri.startswith('ldaps'):
                mock_ldap_tls.assert_called_once()
            else:
                mock_ldap_tls.assert_not_called()


@pytest.mark.parametrize('config', (
    {},
    {'LDAP_URI': 'ldaps://domain.local'},
))
def test_get_exception_users_invalid_config(config):
    """Test that an exception is raised when configuration values are missing."""
    app = create_app('estuary.config.TestAuthConfig')
    app.config.update(config)
    with app.app_context():
        with pytest.raises(InternalServerError):
            _get_exception_users()


@patch('ldap3.Connection')
def test_connection_error(mock_connection):
    """Test that an exception is raised when the LDAP connection fails."""
    mock_connection.return_value.open.side_effect = ldap3.core.exceptions.LDAPSocketOpenError()
    app = create_app('estuary.config.TestAuthConfig')
    app.config['LDAP_URI'] = 'ldaps://domain.local'
    app.config['LDAP_EXCEPTIONS_GROUP_DN'] = 'cn=estuary-exceptions,dc=domain,dc=local'
    with app.app_context():
        with pytest.raises(InternalServerError):
            _get_exception_users()

    mock_connection.return_value.open.assert_called_once()


@patch('ldap3.Connection')
def test_search_failed(mock_connection):
    """Test that an empty set is returned when the search fails."""
    mock_connection.return_value.search.return_value = False
    app = create_app('estuary.config.TestAuthConfig')
    app.config['LDAP_URI'] = 'ldaps://domain.local'
    app.config['LDAP_EXCEPTIONS_GROUP_DN'] = 'cn=estuary-exceptions,dc=domain,dc=local'
    with app.app_context():
        assert _get_exception_users() == set()

    mock_connection.return_value.search.assert_called_once()
