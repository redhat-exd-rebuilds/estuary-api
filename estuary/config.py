# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


class Config(object):
    """The base Estuary application configuration."""

    DEBUG = True
    # We configure logging explicitly, turn off the Flask-supplied log handler.
    LOGGER_HANDLER_POLICY = 'never'
    HOST = '0.0.0.0'
    # This is normally the path for the flask-oidc config, but it isn't used. It must be defined
    # however.
    OIDC_CLIENT_SECRETS = None
    OIDC_RESOURCE_SERVER_ONLY = True
    PRODUCTION = False
    SHOW_DB_URI = False
    SECRET_KEY = 'replace-me-with-something-random'
    NEO4J_URI = 'bolt://neo4j:neo4j@localhost:7687'
    # By default, only allow the front-end on localhost to make cross-origin requests
    CORS_ORIGINS = ['http://localhost:4200']
    STORY_MANAGER_SEQUENCE = ['ModuleStoryManager', 'ContainerStoryManager']
    ENABLE_AUTH = False
    OIDC_INTROSPECT_URL = None
    OIDC_CLIENT_ID = None
    OIDC_CLIENT_SECRET = None
    EMPLOYEE_TYPES = []
    LDAP_CA_CERTIFICATE = '/etc/pki/tls/certs/ca-bundle.crt'
    LDAP_GROUP_MEMBERSHIP_ATTRIBUTE = 'uniqueMember'


class ProdConfig(Config):
    """The production Estuary application configuration."""

    DEBUG = False
    PRODUCTION = True


class DevConfig(Config):
    """The development Estuary application configuration."""

    pass


class TestConfig(Config):
    """The test Estuary application configuration."""

    ENABLE_AUTH = False


class TestAuthConfig(TestConfig):
    """The test Estuary application configuration with authentication configured."""

    OIDC_INTROSPECT_URL = 'https://provider.domain.local/oauth2/default/v1/introspect'
    OIDC_CLIENT_ID = 'estuary'
    OIDC_CLIENT_SECRET = 'some_secret'
    ENABLE_AUTH = True
    EMPLOYEE_TYPES = ['Employee', 'International Local Hire']
