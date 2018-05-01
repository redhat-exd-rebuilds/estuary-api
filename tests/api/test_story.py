# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

from purview.models.koji import KojiBuild
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitCommit
from purview.models.errata import Advisory
from purview.models.freshmaker import FreshmakerEvent, ContainerBuilds
from purview.models.user import User


def test_get_stories(client):
    """Test getting a resource story from Neo4j with its relationships."""
    commit = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 26, 11, 44, 38),
        'commit_date': datetime(2017, 4, 26, 11, 44, 38),
        'hash_': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'log_message': 'Related: #12345 - fix xyz'
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
    bug_two = BugzillaBug.get_or_create({
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
    fm_event = FreshmakerEvent.get_or_create({
        'event_type_id': 8,
        'id_': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt.',
        'url': '/api/1/events/1180'
    })[0]
    cb = ContainerBuilds.get_or_create({
        'build_id': 15639047,
        'event_id': 1180,
        'id_': '397',
        'name': 'jboss-eap-7-eap70-openshift-docker',
        'original_nvr': 'jboss-eap-7-eap70-openshift-docker-1.4-36',
        'rebuilt_nvr': 'jboss-eap-7-eap70-openshift-docker-1.4-36.1522094763',
        'state': 1,
        'state_name': 'DONE',
        'state_reason': 'Built successfully.',
        'time_completed': datetime(2017, 4, 2, 19, 39, 6),
        'time_submitted': datetime(2017, 4, 2, 19, 39, 6),
        'type_': 1,
        'type_name': 'IMAGE',
        'url': '/api/1/builds/397'
    })[0]

    commit.resolved_bugs.connect(bug_two)
    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory)
    advisory.attached_builds.connect(build)
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.triggered_container_builds.connect(cb)

    expected = {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'resource_type': 'BugzillaBug',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'author_date': '2017-04-26T11:44:38+00:00',
                'commit_date': '2017-04-26T11:44:38+00:00',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit'
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at':'2017-04-03T14:47:23+00:00',
                'id':'27825',
                'issue_date':'2017-08-01T05:59:34+00:00',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'resource_type':'Advisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time':'2017-08-01T15:43:51+00:00',
                'synopsis':'cifs-utils bug fix update',
                'type':'RHBA',
                'update_date':'2017-08-01T07:16:00+00:00',
                'updated_at':'2017-08-01T15:43:51+00:00'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'url': '/api/1/events/1180'
            },
            {
                'build_id': 15639047,
                'dep_on': None,
                'event_id': 1180,
                'id': '397',
                'name': 'jboss-eap-7-eap70-openshift-docker',
                'original_nvr': 'jboss-eap-7-eap70-openshift-docker-1.4-36',
                'rebuilt_nvr': 'jboss-eap-7-eap70-openshift-docker-1.4-36.1522094763',
                'resource_type': 'ContainerBuilds',
                'state': 1,
                'state_name': 'DONE',
                'state_reason': 'Built successfully.',
                'time_completed': '2017-04-02T19:39:06+00:00',
                'time_submitted': '2017-04-02T19:39:06+00:00',
                'type': 1,
                'type_name': 'IMAGE',
                'url': '/api/1/builds/397'
            }
        ],
        'meta': {
            'related_nodes': {
                'Advisory': 0,
                'BugzillaBug': 1,
                'DistGitCommit': 0,
                'FreshmakerEvent': 0,
                'KojiBuild': 0
            }
        }
    }

    rv = client.get('/api/v1/story/bugzillabug/12345')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/distgitcommit/8a63adb248ba633e200067e1ad6dc61931727bad')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/kojibuild/2345')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/advisory/27825')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/freshmakerevent/1180')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected

    rv = client.get('/api/v1/story/containerbuilds/397')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_get_artifact_story_not_available(client):
    """Test getting a resource story on a resource that doesn't have any relationships."""
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
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T06:43:58+00:00',
                'id': '5555',
                'modified_time': '2017-12-05T10:12:47+00:00',
                'priority': 'unspecified',
                'product_name': 'Red Hat CloudForms Management Engine',
                'product_version': '5.7.0',
                'resolution': 'WORKSFORME',
                'resource_type': 'BugzillaBug',
                'severity': 'unspecified',
                'short_description': 'Fail to delete OSP tenant by CFME',
                'status': 'CLOSED',
                'target_milestone': 'GA',
                'votes': 0
            }
        ],
        'meta': {
            'related_nodes': {
                'Advisory': 0,
                'BugzillaBug': 0,
                'DistGitCommit': 0,
                'FreshmakerEvent': 0,
                'KojiBuild': 0
            }
        }
    }

    rv = client.get('/api/v1/story/bugzillabug/5555')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_get_stories_not_available(client):
    """Test getting a resource story on a resource that can't have a story."""
    User.get_or_create({'username': 'tbrady'})
    rv = client.get('/api/v1/story/user/tbrady')
    expected = {
        'message': 'The story is not available for this kind of resource',
        'status': 400
    }
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected
