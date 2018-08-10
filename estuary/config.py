# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


class Config(object):
    """The base Estuary application configuration."""

    DEBUG = True
    # We configure logging explicitly, turn off the Flask-supplied log handler.
    LOGGER_HANDLER_POLICY = 'never'
    HOST = '0.0.0.0'
    PRODUCTION = False
    SHOW_DB_URI = False
    SECRET_KEY = 'replace-me-with-something-random'
    NEO4J_URI = 'bolt://neo4j:neo4j@localhost:7687'
    CORS_URL = '*'
    STORY_MANAGER_SEQUENCE = ['ModuleStoryManager', 'ContainerStoryManager']


class ProdConfig(Config):
    """The production Estuary application configuration."""

    DEBUG = False
    PRODUCTION = True


class DevConfig(Config):
    """The development Estuary application configuration."""

    pass


class TestConfig(Config):
    """The test Estuary application configuration."""

    pass
