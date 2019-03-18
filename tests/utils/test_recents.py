# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

import estuary.utils.recents
from estuary.models.koji import KojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory
from estuary.models.freshmaker import FreshmakerEvent


def test_get_recent_nodes():
    """Test the get_recent_nodes function."""
    BugzillaBug.get_or_create({
        'id_': '11111',
        'modified_time': datetime(2017, 4, 26, 11, 44, 38)
    })
    BugzillaBug.get_or_create({
        'id_': '22222',
        'modified_time': datetime(2017, 6, 26, 11, 44, 38)
    })
    BugzillaBug.get_or_create({
        'id_': '33333',
        'modified_time': datetime(2017, 5, 26, 11, 44, 38)
    })
    KojiBuild.get_or_create({
        'id_': '44444',
        'completion_time': datetime(2017, 5, 27, 11, 44, 38)
    })
    DistGitCommit.get_or_create({
        'hash_': '55555',
        'commit_date': datetime(2017, 5, 2, 11, 44, 38)
    })
    Advisory.get_or_create({
        'id_': '66666',
        'update_date': datetime(2017, 5, 30, 11, 44, 38)
    })
    Advisory.get_or_create({
        'id_': '66666',
        'update_date': None
    })
    FreshmakerEvent.get_or_create({
        'id_': '77777'
    })

    ret = estuary.utils.recents.get_recent_nodes()

    assert ret['Advisory'][0]['id'] == '66666'
    assert ret['DistGitCommit'][0]['hash'] == '55555'
    assert ret['FreshmakerEvent'][0]['id'] == '77777'
    assert ret['KojiBuild'][0]['id'] == '44444'
    assert ret['BugzillaBug'][0]['id'] == '22222'
    assert ret['BugzillaBug'][1]['id'] == '33333'
    assert ret['BugzillaBug'][2]['id'] == '11111'
