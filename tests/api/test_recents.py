# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

from estuary.models.koji import KojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory
from estuary.models.freshmaker import FreshmakerEvent


def test_get_recent_nodes(client):
    """Test the get_recent_nodes function."""
    id_dict = {
        FreshmakerEvent.__label__: 'id_',
        BugzillaBug.__label__: 'id_',
        DistGitCommit.__label__: 'hash_',
        KojiBuild.__label__: 'id_',
        Advisory.__label__: 'id_'
    }
    timestamp_dict = {
        FreshmakerEvent.__label__: 'id',
        BugzillaBug.__label__: 'modified_time',
        DistGitCommit.__label__: 'commit_date',
        KojiBuild.__label__: 'completion_time',
        Advisory.__label__: 'update_date'
    }
    expected = {
        'data': {
            'Advisory': [
                {
                    'advisory_name': None,
                    'update_date': '2017-05-30T11:44:38+00:00',
                    'issue_date': None,
                    'created_at': None,
                    'state': None,
                    'product_short_name': None,
                    'product_name': None,
                    'content_types': None,
                    'security_sla': None,
                    'synopsis': None,
                    'security_impact': None,
                    'status_time': None,
                    'actual_ship_date': None,
                    'release_date': None,
                    'id': '66666'
                }
            ],
            'DistGitCommit': [
                {
                    'log_message': None,
                    'author_date': None,
                    'hash': '55555',
                    'commit_date': '2017-05-02T11:44:38+00:00'
                }
            ],
            'FreshmakerEvent': [
                {
                    'state_reason': None,
                    'state_name': None,
                    'id': '77777',
                    'state': None,
                    'event_type_id': None,
                    'message_id': None
                }
            ],
            'KojiBuild': [
                {
                    'name': None,
                    'extra': None,
                    'start_time': None,
                    'creation_time': None,
                    'state': None,
                    'completion_time': '2017-05-27T11:44:38+00:00',
                    'epoch': None,
                    'version': None,
                    'release': None,
                    'id': '44444'
                }
            ],
            'BugzillaBug': [
                {
                    'status': None,
                    'votes': None,
                    'severity': None,
                    'classification': None,
                    'resolution': None,
                    'product_version': None,
                    'creation_time': None,
                    'modified_time': '2017-06-26T11:44:38+00:00',
                    'product_name': None,
                    'priority': None,
                    'short_description': None,
                    'target_milestone': None,
                    'id': '22222'
                },
                {
                    'status': None,
                    'votes': None,
                    'severity': None,
                    'classification': None,
                    'resolution': None,
                    'product_version': None,
                    'creation_time': None,
                    'modified_time': '2017-05-26T11:44:38+00:00',
                    'product_name': None,
                    'priority': None,
                    'short_description': None,
                    'target_milestone': None,
                    'id': '33333'
                },
                {
                    'status': None,
                    'votes': None,
                    'severity': None,
                    'classification': None,
                    'resolution': None,
                    'product_version': None,
                    'creation_time': None,
                    'modified_time': '2017-04-26T11:44:38+00:00',
                    'product_name': None,
                    'priority': None,
                    'short_description': None,
                    'target_milestone': None,
                    'id': '11111'
                }
            ]
        },
        'metadata': {
            'id_keys': id_dict,
            'timestamp_keys': timestamp_dict
        }
    }

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
    FreshmakerEvent.get_or_create({
        'id_': '77777'
    })

    rv = client.get('/api/v1/recents')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected
