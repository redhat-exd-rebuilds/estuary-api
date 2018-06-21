# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import pytest

from estuary.models.koji import KojiBuild, ContainerKojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory
from estuary.models.freshmaker import FreshmakerEvent


@pytest.mark.parametrize('resource,uid,last,expected', [
    ('advisory', '27825', False, [
        {
            'completion_time': '2017-04-02T19:39:06+00:00',
            'creation_time': '2017-04-02T19:39:06+00:00',
            'epoch': '0',
            'extra': None,
            'id': '3456',
            'name': 'slf3j',
            'release': '4.el6_3',
            'resource_type': 'KojiBuild',
            'start_time': '2017-04-02T19:39:06+00:00',
            'state': 2,
            'version': '1.7.1'
        },
        {
            'completion_time': '2017-04-02T19:39:06+00:00',
            'creation_time': '2017-04-02T19:39:06+00:00',
            'epoch': '0',
            'extra': None,
            'id': '2345',
            'name': 'slf4j',
            'release': '4.el7_4',
            'resource_type': 'KojiBuild',
            'start_time': '2017-04-02T19:39:06+00:00',
            'state': 1,
            'version': '1.7.4'
        }
    ]),
    ('freshmakerevent', '1180', True, [
        {
            'completion_time': '2018-04-02T19:39:06+00:00',
            'creation_time': '2018-04-02T19:39:06+00:00',
            'epoch': '0',
            'extra': None,
            'id': '811',
            'name': 'some_build',
            'original_nvr': None,
            'release': '4.el7_4_as',
            'resource_type': 'ContainerKojiBuild',
            'start_time': '2018-04-02T19:39:06+00:00',
            'state': 2,
            'version': '1.7.5'
        },
        {
            'completion_time': '2017-04-02T19:39:06+00:00',
            'creation_time': '2017-04-02T19:39:06+00:00',
            'epoch': '0',
            'extra': None,
            'id': '710',
            'name': 'slf4j_2',
            'original_nvr': None,
            'release': '4.el7_4_as',
            'resource_type': 'ContainerKojiBuild',
            'start_time': '2017-04-02T19:39:06+00:00',
            'state': 1,
            'version': '1.7.4'
        }
    ])
])
def test_node_siblings(client, resource, uid, last, expected):
    """Tests getting the siblings of an artifact's adjacent node in the story path."""
    bug = BugzillaBug.get_or_create({
        'classification': 'Red Hat',
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'id_': '12345',
        'modified_time': datetime(2018, 2, 7, 19, 30, 47),
        'priority': 'high',
        'product_name': 'Red Hat Enterprise Linux',
        'product_version': '7.5',
        'resolution': '',
        'severity': 'low',
        'short_description': 'Some description',
        'status': 'VERIFIED',
        'target_milestone': 'rc',
        'votes': 0
    })[0]
    commit = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 26, 11, 44, 38),
        'commit_date': datetime(2017, 4, 26, 11, 44, 38),
        'hash_': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'log_message': 'Related: #12345 - fix xyz'
    })[0]
    build = KojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '2345',
        'name': 'slf4j',
        'release': '4.el7_4',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.4'
    })[0]
    build_two = KojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '3456',
        'name': 'slf3j',
        'release': '4.el6_3',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 2,
        'version': '1.7.1'
    })[0]
    advisory = Advisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-02',
        'content_types': ['docker'],
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '27825',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'product_short_name': 'RHEL',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'type_': 'RHBA',
        'update_date': datetime(2017, 8, 1, 7, 16),
        'updated_at': datetime(2017, 8, 1, 15, 43, 51)
    })[0]
    fm_event = FreshmakerEvent.get_or_create({
        'event_type_id': 8,
        'id_': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt.',
        'url': '/api/1/events/1180'
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

    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory)
    build_two.advisories.connect(advisory)
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.triggered_container_builds.connect(cb)
    fm_event.triggered_container_builds.connect(cb_two)

    if not last:
        rv = client.get('/api/v1/siblings/{0}/{1}'.format(resource, uid))
    else:
        rv = client.get('/api/v1/siblings/{0}/{1}?last=True'.format(resource, uid))
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_first_node_of_story(client):
    """Tests getting the siblings for the first node of the story."""
    BugzillaBug.get_or_create({
        'classification': 'Red Hat',
        'creation_time': datetime(2017, 4, 2, 6, 43, 58),
        'id_': '5555',
        'modified_time': datetime(2017, 12, 5, 10, 12, 47),
        'priority': 'unspecified',
        'product_name': 'Red Hat CloudForms Management Engine',
        'product_version': '5.7.0',
        'resolution': 'WORKSFORME',
        'severity': 'unspecified',
        'short_description': 'Fail to delete OSP tenant by CFME',
        'status': 'CLOSED',
        'target_milestone': 'GA',
        'votes': 0
    })[0]

    expected = {
        'message': 'Siblings cannot be determined on this kind of resource',
        'status': 400
    }

    rv = client.get('/api/v1/siblings/bugzillabug/5555')
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_last_node_of_story(client):
    """Tests getting the siblings for the last node of the story."""
    ContainerKojiBuild.get_or_create({
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

    expected = {
        'message': 'Siblings cannot be determined on this kind of resource',
        'status': 400
    }

    rv = client.get('/api/v1/siblings/containerkojibuild/710')
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected
