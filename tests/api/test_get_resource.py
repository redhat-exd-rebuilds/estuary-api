# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import pytest

from estuary.models.user import User
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit, DistGitBranch, DistGitRepo
from estuary.models.errata import Advisory
from estuary.models.koji import KojiBuild, KojiTag, ContainerKojiBuild
from estuary.models.freshmaker import FreshmakerEvent, FreshmakerBuild


@pytest.mark.parametrize('resource,uid,expected', [
    ('bugzillabug', '12345', {
        'assignee': {
            'email': 'matt.prahl@domain.local',
            'name': None,
            'username': 'mprahl'
        },
        'attached_advisories': [
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
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time':'2017-08-01T15:43:51+00:00',
                'synopsis':'cifs-utils bug fix update',
                'update_date':'2017-08-01T07:16:00+00:00'
            }
        ],
        'classification':'Red Hat',
        'creation_time':'2017-04-02T19:39:06+00:00',
        'id':'12345',
        'modified_time':'2018-02-07T19:30:47+00:00',
        'priority':'high',
        'product_name':'Red Hat Enterprise Linux',
        'product_version':'7.5',
        'qa_contact':{
            'email': 'jsmith@domain.local',
            'name': None,
            'username': 'jsmith'
        },
        'related_by_commits': [

        ],
        'reporter':{
            'email': 'tom.brady@domain.local',
            'name': None,
            'username': 'tbrady'
        },
        'resolution': '',
        'resolved_by_commits': [
            {
                'author_date': '2017-04-27T11:44:38+00:00',
                'commit_date': '2017-04-27T11:44:38+00:00',
                'hash': '1263adb248ba633e205067e1ad6dc61931727c2d',
                'log_message': 'Related: #12345 - fix xz'
            },
            {
                'author_date': '2017-04-26T11:44:38+00:00',
                'commit_date': '2017-04-26T11:44:38+00:00',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz'
            }
        ],
        'reverted_by_commits': [
            {
                'author_date': '2017-04-27T11:44:38+00:00',
                'commit_date': '2017-04-27T11:44:38+00:00',
                'hash': '5663adb248ba633e205067e1ad6dc61931727123',
                'log_message': 'Revert: #12345'
            }
        ],
        'severity': 'low',
        'short_description': 'Some description',
        'status': 'VERIFIED',
        'target_milestone': 'rc',
        'votes': 0
    }),
    ('distgitcommit', '8a63adb248ba633e200067e1ad6dc61931727bad', {
        'author': {
            'email': 'tom.brady@domain.local',
            'name': None,
            'username': 'tbrady'
        },
        'author_date': '2017-04-26T11:44:38+00:00',
        'branches': [
            {
                'name': 'some_branch_name',
                'repo_name': 'some_repo_name',
                'repo_namespace': 'some_repo_namespace'
            }
        ],
        'children': [
            {
                'author_date': '2017-04-27T11:44:38+00:00',
                'commit_date': '2017-04-27T11:44:38+00:00',
                'hash': '5663adb248ba633e205067e1ad6dc61931727123',
                'log_message': 'Revert: #12345'
            }
        ],
        'commit_date': '2017-04-26T11:44:38+00:00',
        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'koji_builds': [

        ],
        'log_message':'Related: #12345 - fix xyz',
        'parent':{
            'author_date': '2017-04-27T11:44:38+00:00',
            'commit_date': '2017-04-27T11:44:38+00:00',
            'hash': '1263adb248ba633e205067e1ad6dc61931727c2d',
            'log_message': 'Related: #12345 - fix xz'
        },
        'related_bugs': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '272895',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'low',
                'product_name': 'Satellite',
                'product_version': '3',
                'resolution': '',
                'severity': 'medium',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            }
        ],
        'repos': [
            {
                'name': 'some_repo',
                'namespace': 'some_namespace'
            }
        ],
        'resolved_bugs': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '67890',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'medium',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.3',
                'resolution': '',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            }
        ],
        'reverted_bugs': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '67890',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'medium',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.3',
                'resolution': '',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            }
        ]
    }),
    ('kojibuild', '2345', {
        'advisories': [

        ],
        'commit':{
            'author_date': '2017-04-27T11:44:38+00:00',
            'commit_date': '2017-04-27T11:44:38+00:00',
            'hash': '1263adb248ba633e205067e1ad6dc61931727c2d',
            'log_message': 'Related: #12345 - fix xz'
        },
        'completion_time': '2017-04-02T19:39:06+00:00',
        'creation_time': '2017-04-02T19:39:06+00:00',
        'epoch': '0',
        'extra': None,
        'id': '2345',
        'module_builds': [],
        'name': 'slf4j',
        'owner': {
            'email': 'matt.prahl@domain.local',
            'name': None,
            'username': 'mprahl'
        },
        'release': '4.el7_4',
        'start_time': '2017-04-02T19:39:06+00:00',
        'state': 1,
        'tags': [
            {
                'id': '2702',
                'name': 'some_active_tag'
            }
        ],
        'version': '1.7.4'
    }),
    ('advisory', '27825', {
        'actual_ship_date': '2017-08-01T15:43:51+00:00',
        'advisory_name': 'RHBA-2017:2251-02',
        'assigned_to': {
            'email': 'matt.prahl@domain.local',
            'name': None,
            'username': 'mprahl'
        },
        'attached_bugs': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47+00:00',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            }
        ],
        'attached_builds': [
            {
                'completion_time': '2017-04-02T19:39:06+00:00',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'start_time': '2017-04-02T19:39:06+00:00',
                'state': 1,
                'version': '1.7.4'
            }
        ],
        'content_types': [
            'docker'
        ],
        'created_at':'2017-04-03T14:47:23+00:00',
        'id':'27825',
        'issue_date':'2017-08-01T05:59:34+00:00',
        'product_name': 'Red Hat Enterprise Linux',
        'product_short_name': 'RHEL',
        'release_date': None,
        'reporter': {
            'email': 'jsmith@domain.local',
            'name': None,
            'username': 'jsmith'
        },
        'security_impact': 'None',
        'security_sla': None,
        'state': 'SHIPPED_LIVE',
        'status_time': '2017-08-01T15:43:51+00:00',
        'synopsis': 'cifs-utils bug fix update',
        'triggered_freshmaker_event': [

        ],
        'update_date':'2017-08-01T07:16:00+00:00'
    }),
    ('freshmakerevent', '1180', {
        'event_type_id': 8,
        'id': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'requested_builds': [{
            'build_id': 15639305,
            'dep_on': 'jboss-eap-7-eap70-openshift-docker',
            'id': '398',
            'name': 'metrics-hawkular-metrics-docker',
            'original_nvr': 'metrics-hawkular-metrics-docker-v3.7.23-10',
            'rebuilt_nvr': 'metrics-hawkular-metrics-docker-v3.7.23-10.1522094767',
            'state': 1,
            'state_name': 'DONE',
            'state_reason': 'Built successfully.',
            'time_completed': '2017-04-02T19:39:06+00:00',
            'time_submitted': '2017-04-02T19:39:06+00:00',
            'type': 1,
            'type_name': 'IMAGE',
            'url': '/api/1/builds/398'
        }],
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt',
        'time_created': '2019-08-21T13:42:20+00:00',
        'time_done': '2099-08-21T13:42:20+00:00',
        'triggered_by_advisory': {
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
            'security_impact':'None',
            'security_sla':None,
            'state':'SHIPPED_LIVE',
            'status_time':'2017-08-01T15:43:51+00:00',
            'synopsis':'cifs-utils bug fix update',
            'update_date':'2017-08-01T07:16:00+00:00'
        },
        'successful_koji_builds': [{
            'completion_time': '2017-04-02T19:39:06+00:00',
            'creation_time': '2017-04-02T19:39:06+00:00',
            'epoch': '0',
            'extra': None,
            'id': '710',
            'name': 'slf4j_2',
            'original_nvr': None,
            'release': '4.el7_4_as',
            'start_time': '2017-04-02T19:39:06+00:00',
            'state': 1,
            'version': '1.7.4'}]
    }),
    ('containerkojibuild', '710', {
        'advisories': [

        ],
        'commit':None,
        'completion_time':'2017-04-02T19:39:06+00:00',
        'creation_time':'2017-04-02T19:39:06+00:00',
        'epoch':'0',
        'extra':None,
        'id':'710',
        'name':'slf4j_2',
        'module_builds': [],
        'original_nvr': None,
        'owner':None,
        'release':'4.el7_4_as',
        'start_time':'2017-04-02T19:39:06+00:00',
        'state':1,
        'tags':[],
        'triggered_by_freshmaker_event':None,
        'version':'1.7.4'
    })
])
def test_get_resources(client, resource, uid, expected):
    """Test getting a resource from Neo4j with its relationships."""
    tbrady = User.get_or_create({
        'email': 'tom.brady@domain.local',
        'username': 'tbrady'
    })[0]
    mprahl = User.get_or_create({
        'email': 'matt.prahl@domain.local',
        'username': 'mprahl'
    })[0]
    jsmith = User.get_or_create({
        'email': 'jsmith@domain.local',
        'username': 'jsmith'
    })[0]
    commit = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 26, 11, 44, 38),
        'commit_date': datetime(2017, 4, 26, 11, 44, 38),
        'hash_': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'log_message': 'Related: #12345 - fix xyz'
    })[0]
    commit_two = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 27, 11, 44, 38),
        'commit_date': datetime(2017, 4, 27, 11, 44, 38),
        'hash_': '1263adb248ba633e205067e1ad6dc61931727c2d',
        'log_message': 'Related: #12345 - fix xz'
    })[0]
    commit_three = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 27, 11, 44, 38),
        'commit_date': datetime(2017, 4, 27, 11, 44, 38),
        'hash_': '5663adb248ba633e205067e1ad6dc61931727123',
        'log_message': 'Revert: #12345'
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
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'id_': '67890',
        'modified_time': datetime(2018, 2, 7, 19, 30, 47),
        'priority': 'medium',
        'product_name': 'Red Hat Enterprise Linux',
        'product_version': '7.3',
        'resolution': '',
        'severity': 'low',
        'short_description': 'Some description',
        'status': 'VERIFIED',
        'target_milestone': 'rc',
        'votes': 0
    })[0]
    bug_three = BugzillaBug.get_or_create({
        'classification': 'Red Hat',
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'id_': '272895',
        'modified_time': datetime(2018, 2, 7, 19, 30, 47),
        'priority': 'low',
        'product_name': 'Satellite',
        'product_version': '3',
        'resolution': '',
        'severity': 'medium',
        'short_description': 'Some description',
        'status': 'VERIFIED',
        'target_milestone': 'rc',
        'votes': 0
    })[0]
    repo = DistGitRepo.get_or_create({
        'name': 'some_repo',
        'namespace': 'some_namespace',
    })[0]
    branch = DistGitBranch.get_or_create({
        'name': 'some_branch_name',
        'repo_name': 'some_repo_name',
        'repo_namespace': 'some_repo_namespace'
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
    tag = KojiTag.get_or_create({
        'id_': '2702',
        'name': 'some_active_tag'
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
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]
    fm_event = FreshmakerEvent.get_or_create({
        'event_type_id': 8,
        'id_': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt',
        'time_created': datetime(2019, 8, 21, 13, 42, 20),
        'time_done': datetime(2099, 8, 21, 13, 42, 20)
    })[0]
    fm_build = FreshmakerBuild.get_or_create({
        'id_': 398,
        'build_id': 15639305,
        'dep_on': "jboss-eap-7-eap70-openshift-docker",
        'name': "metrics-hawkular-metrics-docker",
        'original_nvr': "metrics-hawkular-metrics-docker-v3.7.23-10",
        'rebuilt_nvr': "metrics-hawkular-metrics-docker-v3.7.23-10.1522094767",
        'state': 1,
        'state_name': "DONE",
        'state_reason': "Built successfully.",
        'time_completed': datetime(2017, 4, 2, 19, 39, 6),
        'time_submitted': datetime(2017, 4, 2, 19, 39, 6),
        'type_': 1,
        'type_name': "IMAGE",
        'url': "/api/1/builds/398"
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

    if resource == 'bugzillabug':
        bug.assignee.connect(mprahl)
        bug.qa_contact.connect(jsmith)
        bug.reporter.connect(tbrady)
        commit.resolved_bugs.connect(bug)
        commit_two.resolved_bugs.connect(bug)
        commit_three.reverted_bugs.connect(bug)
        advisory.attached_bugs.connect(bug)

    if resource == 'distgitcommit':
        commit.author.connect(tbrady)
        commit.parent.connect(commit_two)
        commit_three.parent.connect(commit)
        commit.related_bugs.connect(bug)
        commit.related_bugs.connect(bug_three)
        commit.reverted_bugs.connect(bug_two)
        repo.commits.connect(commit)
        branch.commits.connect(commit)
        commit.resolved_bugs.connect(bug)
        commit.resolved_bugs.connect(bug_two)

    if resource == 'kojibuild':
        build.owner.connect(mprahl)
        build.commit.connect(commit_two)
        tag.builds.connect(build)

    if resource == 'advisory':
        advisory.assigned_to.connect(mprahl)
        advisory.reporter.connect(jsmith)
        advisory.attached_builds.connect(build)
        advisory.attached_bugs.connect(bug)

    if resource == 'freshmakerevent':
        fm_event.triggered_by_advisory.connect(advisory)
        fm_event.successful_koji_builds.connect(cb)
        fm_event.requested_builds.connect(fm_build)

    if resource == 'containerbuild':
        fm_event.successful_koji_builds.connect(cb)

    rv = client.get('/api/v1/{0}/{1}'.format(resource, uid))
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected
