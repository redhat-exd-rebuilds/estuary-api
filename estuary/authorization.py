# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import ssl

from flask import current_app
from werkzeug.exceptions import InternalServerError

from estuary import log


def is_user_authorized(username, employee_type):
    """
    Verify the user is authorized to access the application.

    :param str username: the username from the user's token
    :param str employee_type: the employee type from the user's token
    :return: a boolean that determines if the user is authorized
    :rtype: bool
    """
    employee_types = current_app.config.get('EMPLOYEE_TYPES', [])
    if employee_type in employee_types:
        log.debug('The user %s is an employee', username)
        return True

    ldap_group_dn = current_app.config.get('LDAP_EXCEPTIONS_GROUP_DN')
    if ldap_group_dn and username in _get_exception_users():
        log.debug('The user %s is not considered an employee but is an exception', username)
        return True

    return False


def _get_exception_users():
    """
    Get the list of users that are explicitly whitelisted.

    If the LDAP search fails, an empty set is returned.

    :return: a set of usernames
    :rtype: set
    :raise InternalServerError: if a required configuration value is not set or the connection to
        the LDAP server fails
    """
    # Import this here so it's not required for deployments with auth disabled
    import ldap3

    base_error = '%s is not set in the server configuration'
    ldap_uri = current_app.config.get('LDAP_URI')
    if not ldap_uri:
        log.error(base_error, 'LDAP_URI')
        raise InternalServerError()

    ldap_group_dn = current_app.config.get('LDAP_EXCEPTIONS_GROUP_DN')
    if not ldap_group_dn:
        log.error(base_error, 'LDAP_EXCEPTIONS_GROUP_DN')
        raise InternalServerError()

    if ldap_uri.startswith('ldaps://'):
        ca = current_app.config['LDAP_CA_CERTIFICATE']
        log.debug('Connecting to %s using SSL and the CA %s', ldap_uri, ca)
        tls = ldap3.Tls(ca_certs_file=ca, validate=ssl.CERT_REQUIRED)
        server = ldap3.Server(ldap_uri, use_ssl=True, tls=tls)
    else:
        log.debug('Connecting to %s without SSL', ldap_uri)
        server = ldap3.Server(ldap_uri)

    connection = ldap3.Connection(server)
    try:
        connection.open()
    except ldap3.core.exceptions.LDAPSocketOpenError:
        log.exception('The connection to %s failed', ldap_uri)
        raise InternalServerError()

    membership_attr = current_app.config['LDAP_GROUP_MEMBERSHIP_ATTRIBUTE']
    log.debug('Searching for the attribute %s on %s', ldap_group_dn, membership_attr)
    # Set the scope to base so only the group from LDAP_GROUP_DN is returned
    success = connection.search(
        ldap_group_dn, '(cn=*)', search_scope=ldap3.BASE, attributes=[membership_attr])
    if not success:
        log.error(
            'The user exceptions list could not be determined because the search for the attribute '
            '%s on %s failed with %r',
            membership_attr, ldap_group_dn, connection.response,
        )
        return set()

    return set([
        dn.split('=')[1].split(',')[0]
        for dn in connection.response[0]['attributes'][membership_attr]
    ])
