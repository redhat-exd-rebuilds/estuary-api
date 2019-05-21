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

    nodes, meta = estuary.utils.recents.get_recent_nodes()

    assert nodes['Advisory'][0]['id'] == '66666'
    assert nodes['DistGitCommit'][0]['hash'] == '55555'
    assert nodes['FreshmakerEvent'][0]['id'] == '77777'
    assert nodes['KojiBuild'][0]['id'] == '44444'
    assert nodes['BugzillaBug'][0]['id'] == '22222'
    assert nodes['BugzillaBug'][1]['id'] == '33333'
    assert nodes['BugzillaBug'][2]['id'] == '11111'

    id_dict = {
        FreshmakerEvent.__label__: 'id',
        BugzillaBug.__label__: 'id',
        DistGitCommit.__label__: 'hash',
        KojiBuild.__label__: 'id',
        Advisory.__label__: 'id'
    }
    timestamp_dict = {
        FreshmakerEvent.__label__: 'id',
        BugzillaBug.__label__: 'modified_time',
        DistGitCommit.__label__: 'commit_date',
        KojiBuild.__label__: 'completion_time',
        Advisory.__label__: 'update_date'
    }

    assert meta['id_keys'] == id_dict
    assert meta['timestamp_keys'] == timestamp_dict
