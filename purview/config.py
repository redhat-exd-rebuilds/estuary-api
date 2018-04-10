# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals


class Config(object):
    """
    A Purview Flask configuration
    """
    DEBUG = True
    # We configure logging explicitly, turn off the Flask-supplied log handler.
    LOGGER_HANDLER_POLICY = 'never'
    HOST = '0.0.0.0'
    PRODUCTION = False
    SHOW_DB_URI = False
    SECRET_KEY = 'replace-me-with-something-random'
    NEO4J_URI = 'bolt://neo4j:neo4j@localhost:7687'


class ProdConfig(Config):
    DEBUG = False
    PRODUCTION = True


class DevConfig(Config):
    pass


class TestConfig(Config):
    pass
