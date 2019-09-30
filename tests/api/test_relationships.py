# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import pytest

from estuary.models.freshmaker import FreshmakerEvent
from estuary.models.koji import ContainerKojiBuild


@pytest.mark.parametrize('resource,uid,relationship,expected', [
    ('freshmakerevent', '1180', 'successful_koji_builds', {
        'data': [
            {
                'advisories': [

                ],
                'commit': None,
                'completion_time': '2018-04-02T19:39:06Z',
                'creation_time': '2018-04-02T19:39:06Z',
                'epoch': '1',
                'extra': None,
                'id': '2011',
                'module_builds': [],
                'name': 'some_other_build',
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_6_a',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'some_other_build-1.7.6-4.el7_6_a',
                'start_time': '2018-04-02T19:39:06Z',
                'state':1,
                'tags':[

                ],
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'resource_type': 'FreshmakerEvent',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.6'
            },
            {
                'advisories': [

                ],
                'commit': None,
                'completion_time': '2018-04-02T19:39:06Z',
                'creation_time': '2018-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '811',
                'module_builds': [],
                'name': 'some_build',
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'some_build-1.7.5-4.el7_4_as',
                'start_time': '2018-04-02T19:39:06Z',
                'state':2,
                'tags':[

                ],
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'resource_type': 'FreshmakerEvent',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.5'
            },
            {
                'advisories': [

                ],
                'commit': None,
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'module_builds': [],
                'name': 'slf4j_2',
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state':1,
                'tags':[

                ],
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'resource_type': 'FreshmakerEvent',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.4'
            }
        ],
        'meta': {
            'description': 'successful koji builds of Freshmaker event 1180'
        }
    })
])
def test_one_to_many_node_relationships(client, resource, uid, relationship, expected):
    """Tests getting one-to-many relationships of an artifact."""
    fm_event = FreshmakerEvent.get_or_create({
        'event_type_id': 8,
        'id_': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt.',
        'time_created': datetime(2019, 8, 21, 13, 42, 20),
        'time_done': datetime(2099, 8, 21, 13, 42, 20)
    })[0]
    cb = ContainerKojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '710',
        'name': 'slf4j_2',
        'release': '4.el7_4_as',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.4'
    })[0]
    cb_two = ContainerKojiBuild.get_or_create({
        'completion_time': datetime(2018, 4, 2, 19, 39, 6),
        'creation_time': datetime(2018, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '811',
        'name': 'some_build',
        'release': '4.el7_4_as',
        'start_time': datetime(2018, 4, 2, 19, 39, 6),
        'state': 2,
        'version': '1.7.5'
    })[0]
    cb_three = ContainerKojiBuild.get_or_create({
        'completion_time': datetime(2018, 4, 2, 19, 39, 6),
        'creation_time': datetime(2018, 4, 2, 19, 39, 6),
        'epoch': '1',
        'id_': '2011',
        'name': 'some_other_build',
        'release': '4.el7_6_a',
        'start_time': datetime(2018, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.6'
    })[0]

    fm_event.successful_koji_builds.connect(cb)
    fm_event.successful_koji_builds.connect(cb_two)
    fm_event.successful_koji_builds.connect(cb_three)

    rv = client.get('/api/v1/relationships/{0}/{1}/{2}'.format(resource, uid, relationship))
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_one_to_many_node_relationships_failed(client):
    """Tests getting one-to-many relationships of an artifact with wrong relationship name."""
    fm_event = FreshmakerEvent.get_or_create({
        'event_type_id': 8,
        'id_': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt.',
        'time_created': datetime(2019, 8, 21, 13, 42, 20),
        'time_done': datetime(2099, 8, 21, 13, 42, 20)
    })[0]
    cb = ContainerKojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '710',
        'name': 'slf4j_2',
        'release': '4.el7_4_as',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.4'
    })[0]

    fm_event.successful_koji_builds.connect(cb)

    expected = {
        'message': 'Please provide a valid relationship name for freshmakerevent with uid 1180',
        'status': 400
    }

    rv = client.get('/api/v1/relationships/freshmakerevent/1180/some_non-existent_relationship')
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected
