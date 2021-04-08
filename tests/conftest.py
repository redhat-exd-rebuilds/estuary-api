# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import os

import pytest
from neomodel import config as neomodel_config
from neomodel import db as neo4j_db

from estuary.app import create_app


@pytest.fixture(scope='session')
def client():
    """Pytest fixture that creates a Flask application object for the pytest session."""
    return create_app('estuary.config.TestConfig').test_client()


# Reinitialize Neo4j before each test
@pytest.fixture(autouse=True)
def run_before_tests():
    """Pytest fixture that prepares the environment before each test."""
    # Code that runs before each test
    neomodel_config.DATABASE_URL = os.environ.get(
        'NEO4J_BOLT_URL', 'bolt://neo4j:neo4j@localhost:7687'
    )
    neomodel_config.AUTO_INSTALL_LABELS = True
    neo4j_db.cypher_query('MATCH (a) DETACH DELETE a')
