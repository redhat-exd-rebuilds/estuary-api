# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


class Config(object):
    """The base Purview application configuration."""

    DEBUG = True
    # We configure logging explicitly, turn off the Flask-supplied log handler.
    LOGGER_HANDLER_POLICY = 'never'
    HOST = '0.0.0.0'
    PRODUCTION = False
    SHOW_DB_URI = False
    SECRET_KEY = 'replace-me-with-something-random'
    NEO4J_URI = 'bolt://neo4j:neo4j@localhost:7687'


class ProdConfig(Config):
    """The production Purview application configuration."""

    DEBUG = False
    PRODUCTION = True


class DevConfig(Config):
    """The development Purview application configuration."""

    pass


class TestConfig(Config):
    """The test Purview application configuration."""

    pass
