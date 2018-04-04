# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import pytest

from purview.app import create_app


@pytest.fixture(scope='session')
def client():
    return create_app('purview.config.TestConfig').test_client()
