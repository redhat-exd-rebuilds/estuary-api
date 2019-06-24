# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import pytest
from six.moves import urllib

from estuary.models.koji import KojiBuild, ContainerKojiBuild, ModuleKojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit, DistGitRepo, DistGitBranch
from estuary.models.errata import Advisory, ContainerAdvisory
from estuary.models.freshmaker import FreshmakerEvent, FreshmakerBuild
from estuary.models.user import User


@pytest.mark.parametrize('resource,uids,expected', [
    ('bugzillabug', ['12345', '#12345', 'RHBZ#12345', 'rhbz#12345'], {
        'data': [
            {
                'assignee': None,
                'attached_advisories': [

                ],
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'qa_contact': None,
                'related_by_commits': [

                ],
                'reporter': None,
                'resolution': '',
                'resolved_by_commits': [
                    {
                        'author_date': '2017-04-26T11:44:38Z',
                        'commit_date': '2017-04-26T11:44:38Z',
                        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                        'log_message': 'Related: #12345 - fix xyz'
                    }
                ],
                'resource_type': 'BugzillaBug',
                'display_name': 'RHBZ#12345',
                'reverted_by_commits': [

                ],
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes':0
            },
            {
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit',
                'display_name': 'commit #8a63adb',
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'display_name':'RHBA-2017:2251-02',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'display_name': 'Freshmaker event 1180',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 0,
            'story_type': 'container'
        }
    }),
    ('distgitcommit', ['8a63adb248ba633e200067e1ad6dc61931727bad'], {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'resource_type': 'BugzillaBug',
                'display_name': 'RHBZ#12345',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'author': None,
                'author_date': '2017-04-26T11:44:38Z',
                'branches': [{
                    'name': 'some-branch',
                    'repo_name': 'slf4j',
                    'repo_namespace': 'rpms'
                }],
                'children': [

                ],
                'commit_date': '2017-04-26T11:44:38Z',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'koji_builds': [
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'epoch': '0',
                        'extra': None,
                        'id': '2345',
                        'name': 'slf4j',
                        'release': '4.el7_4',
                        'start_time': '2017-04-02T19:39:06Z',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ],
                'log_message': 'Related: #12345 - fix xyz',
                'parent': None,
                'related_bugs': [

                ],
                'repos': [{
                    'name': 'slf4j',
                    'namespace': 'rpms'
                }],
                'resolved_bugs': [
                    {
                        'classification': 'Red Hat',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'id': '12345',
                        'modified_time': '2018-02-07T19:30:47Z',
                        'priority': 'high',
                        'product_name': 'Red Hat Enterprise Linux',
                        'product_version': '7.5',
                        'resolution': '',
                        'severity': 'low',
                        'short_description': 'Some description',
                        'status': 'VERIFIED',
                        'target_milestone': 'rc',
                        'votes': 0
                    },
                    {
                        'classification': 'Red Hat',
                        'creation_time': '2017-04-02T06:43:58Z',
                        'id': '5555',
                        'modified_time': '2017-12-05T10:12:47Z',
                        'priority': 'unspecified',
                        'product_name': 'Red Hat CloudForms Management Engine',
                        'product_version': '5.7.0',
                        'resolution': 'WORKSFORME',
                        'severity': 'unspecified',
                        'short_description': 'Fail to delete OSP tenant by CFME',
                        'status': 'CLOSED',
                        'target_milestone': 'GA',
                        'votes': 0
                    }
                ],
                'resource_type': 'DistGitCommit',
                'display_name': 'commit #8a63adb',
                'reverted_bugs': [

                ]
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'display_name':'RHBA-2017:2251-02',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'display_name': 'Freshmaker event 1180',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 1,
            'story_type': 'container'
        }
    }),
    ('kojibuild', ['2345', 'slf4j-1.7.4-4.el7_4', 'slf4j-1.7.4-4.el7_4.src.rpm'], {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'resource_type': 'BugzillaBug',
                'display_name': 'RHBZ#12345',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit',
                'display_name': 'commit #8a63adb',
            },
            {
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51Z',
                        'advisory_name': 'RHBA-2017:2251-02',
                        'content_types': [
                            'docker'
                        ],
                        'created_at': '2017-04-03T14:47:23Z',
                        'id': '27825',
                        'issue_date': '2017-08-01T05:59:34Z',
                        'product_name': 'Red Hat Enterprise Linux',
                        'product_short_name': 'RHEL',
                        'release_date': None,
                        'security_impact': 'None',
                        'security_sla': None,
                        'state': 'SHIPPED_LIVE',
                        'status_time': '2017-08-01T15:43:51Z',
                        'synopsis': 'cifs-utils bug fix update',
                        'update_date': '2017-08-01T07:16:00Z'
                    }
                ],
                'commit':{
                    'author_date': '2017-04-26T11:44:38Z',
                    'commit_date': '2017-04-26T11:44:38Z',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz'
                },
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'module_builds': [],
                'name': 'slf4j',
                'owner': None,
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'tags': [

                ],
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'display_name':'RHBA-2017:2251-02',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'display_name': 'Freshmaker event 1180',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 2,
            'story_type': 'container'
        }
    }),
    ('advisory', ['27825', 'RHBA-2017:2251-02', 'RHBA-2017:2251'], {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'resource_type': 'BugzillaBug',
                'display_name': 'RHBZ#12345',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit',
                'display_name': 'commit #8a63adb',
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'assigned_to': None,
                'attached_bugs': [

                ],
                'attached_builds': [
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'epoch': '0',
                        'extra': None,
                        'id': '2345',
                        'name': 'slf4j',
                        'release': '4.el7_4',
                        'start_time': '2017-04-02T19:39:06Z',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ],
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-02',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'reporter': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'triggered_freshmaker_event': [
                    {
                        'event_type_id': 8,
                        'id': '1180',
                        'message_id': 'ID:messaging-devops-broker01.test',
                        'state': 2,
                        'state_name': 'COMPLETE',
                        'state_reason': 'All container images have been rebuilt.',
                        'time_created': '2019-08-21T13:42:20Z',
                        'time_done': '2099-08-21T13:42:20Z'
                    }
                ],
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'display_name': 'Freshmaker event 1180',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 3,
            'story_type': 'container'
        }
    }),
    ('freshmakerevent', ['1180'], {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
                'priority': 'high',
                'product_name': 'Red Hat Enterprise Linux',
                'product_version': '7.5',
                'resolution': '',
                'resource_type': 'BugzillaBug',
                'display_name': 'RHBZ#12345',
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes': 0
            },
            {
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit',
                'display_name': 'commit #8a63adb',
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-02',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
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
                    'time_completed': '2017-04-02T19:39:06Z',
                    'time_submitted': '2017-04-02T19:39:06Z',
                    'type': 1,
                    'type_name': 'IMAGE',
                    'url': '/api/1/builds/398'
                }],
                'resource_type': 'FreshmakerEvent',
                'display_name': 'Freshmaker event 1180',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z',
                'triggered_by_advisory': {
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2017-04-03T14:47:23Z',
                    'id': '27825',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name': 'Red Hat Enterprise Linux',
                    'product_short_name': 'RHEL',
                    'release_date': None,
                    'security_impact': 'None',
                    'security_sla': None,
                    'state': 'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51Z',
                    'synopsis': 'cifs-utils bug fix update',
                    'update_date': '2017-08-01T07:16:00Z'
                },
                'successful_koji_builds': [
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'epoch': '0',
                        'extra': None,
                        'id': '710',
                        'name': 'slf4j_2',
                        'original_nvr': None,
                        'release': '4.el7_4_as',
                        'start_time': '2017-04-02T19:39:06Z',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ]
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'display_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 4,
            'story_type': 'container'
        }
    }),
    ('containerkojibuild', ['710'], {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'RHBZ#12345',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
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
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'display_name': 'commit #8a63adb',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-02',
                'id':'27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'resource_type':'Advisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis':'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
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
            {
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51Z',
                        'advisory_name': 'RHBA-2017:2251-03',
                        'content_types': [
                            'docker'
                        ],
                        'created_at': '2017-04-03T14:47:23Z',
                        'id':'12327',
                        'issue_date': '2017-08-01T05:59:34Z',
                        'product_name':'Red Hat Enterprise Linux',
                        'product_short_name':'RHEL',
                        'release_date':None,
                        'security_impact':'None',
                        'security_sla':None,
                        'state':'SHIPPED_LIVE',
                        'status_time': '2017-08-01T15:43:51Z',
                        'synopsis':'cifs-utils bug fix update',
                        'update_date': '2017-08-01T07:16:00Z'
                    }
                ],
                'commit':None,
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name':'slf4j_2-1.7.4-4.el7_4_as',
                'epoch':'0',
                'extra':None,
                'id':'710',
                'module_builds': [],
                'name':'slf4j_2',
                'original_nvr':None,
                'owner':None,
                'release':'4.el7_4_as',
                'resource_type':'ContainerKojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state':1,
                'tags':[

                ],
                'triggered_by_freshmaker_event':{
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id':'12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'resource_type':'ContainerAdvisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis':'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta':{
            'requested_node_index': 5,
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'story_type': 'container'
        }
    }),
    ('containeradvisory', ['12327'], {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'RHBZ#12345',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
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
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'display_name': 'commit #8a63adb',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit',
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-02',
                'id':'27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'resource_type':'Advisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis':'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
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
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'assigned_to': None,
                'attached_bugs': [

                ],
                'attached_builds':[
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'epoch': '0',
                        'extra': None,
                        'id': '710',
                        'name': 'slf4j_2',
                        'original_nvr': None,
                        'release': '4.el7_4_as',
                        'start_time': '2017-04-02T19:39:06Z',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ],
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id':'12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'reporter':None,
                'resource_type':'ContainerAdvisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis':'cifs-utils bug fix update',
                'triggered_freshmaker_event':[

                ],
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta':{
            'requested_node_index': 6,
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'story_type': 'container'
        }
    })
])
def test_get_stories(client, resource, uids, expected):
    """Test getting a resource story from Neo4j with its relationships."""
    commit = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 26, 11, 44, 38),
        'commit_date': datetime(2017, 4, 26, 11, 44, 38),
        'hash_': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'log_message': 'Related: #12345 - fix xyz'
    })[0]
    branch = DistGitBranch.get_or_create({
        'name': 'some-branch',
        'repo_name': 'slf4j',
        'repo_namespace': 'rpms'
    })[0]
    repo = DistGitRepo.get_or_create({
        'name': 'slf4j',
        'namespace': 'rpms'
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
    containeradvisory = ContainerAdvisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-03',
        'content_types': ['docker'],
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '12327',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'product_short_name': 'RHEL',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]

    repo.branches.connect(branch)
    repo.commits.connect(commit)
    branch.commits.connect(commit)
    commit.resolved_bugs.connect(bug_two)
    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory)
    advisory.attached_builds.connect(build)
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.successful_koji_builds.connect(cb)
    fm_event.requested_builds.connect(fm_build)
    containeradvisory.attached_builds.connect(cb)

    for uid in uids:
        url = '/api/v1/story/{0}/{1}'.format(resource, urllib.parse.quote(uid))
        rv = client.get(url)
        assert rv.status_code == 200
        assert json.loads(rv.data.decode('utf-8')) == expected


@pytest.mark.parametrize('resource,uid,expected', [
    ('freshmakerevent', 1180, {
        'data': [
            {
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'RHBZ#12345',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47Z',
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
                'author_date': '2017-04-26T11:44:38Z',
                'commit_date': '2017-04-26T11:44:38Z',
                'display_name': 'commit #8a63adb',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'log_message': 'Related: #12345 - fix xyz',
                'resource_type': 'DistGitCommit'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'context': 'a2037af3',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': '389-ds-None-20180805121332.a2037af3',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'mbs_id': 1338,
                'module_name': '389-ds',
                'module_stream': '1.4',
                'module_version': '20180805121332',
                'name': '389-ds',
                'release': '20180805121332.a2037af3',
                'resource_type': 'ModuleKojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': None,
                'version': None
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-02',
                'id':'27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date': None,
                'resource_type':'Advisory',
                'security_impact':'None',
                'security_sla': None,
                'state':'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis':'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
                'display_name': 'Freshmaker event 1180',
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
                    'time_completed': '2017-04-02T19:39:06Z',
                    'time_submitted': '2017-04-02T19:39:06Z',
                    'type': 1,
                    'type_name': 'IMAGE',
                    'url': '/api/1/builds/398'
                }],
                'resource_type': 'FreshmakerEvent',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z',
                'triggered_by_advisory': {
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2017-04-03T14:47:23Z',
                    'id':'27825',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name':'Red Hat Enterprise Linux',
                    'product_short_name':'RHEL',
                    'release_date': None,
                    'security_impact':'None',
                    'security_sla': None,
                    'state':'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51Z',
                    'synopsis':'cifs-utils bug fix update',
                    'update_date': '2017-08-01T07:16:00Z'
                },
                'successful_koji_builds':[
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'epoch': '0',
                        'extra': None,
                        'id': '710',
                        'name': 'slf4j_2',
                        'original_nvr': None,
                        'release': '4.el7_4_as',
                        'start_time': '2017-04-02T19:39:06Z',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ]
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'epoch': '0',
                'extra': None,
                'id': '710',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'display_name':'RHBA-2017:2251-03',
                'id':'12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date': None,
                'resource_type':'ContainerAdvisory',
                'security_impact':'None',
                'security_sla': None,
                'state':'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis':'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'requested_node_index': 5,
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_forward': [0, 0, 0, 0, 0, 0, 0, 0],
            'story_type': 'module'
        }
    })
])
def test_module_story_flow(client, resource, uid, expected):
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
        'update_date': datetime(2017, 8, 1, 7, 16)
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
    module_build = ModuleKojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '2345',
        'name': '389-ds',
        'context': 'a2037af3',
        'release': '20180805121332.a2037af3',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'mbs_id': 1338,
        'module_name': '389-ds',
        'module_version': '20180805121332',
        'module_stream': '1.4'
    })[0]
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
    containeradvisory = ContainerAdvisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-03',
        'content_types': ['docker'],
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '12327',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'product_short_name': 'RHEL',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]

    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory)
    advisory.attached_builds.connect(build)
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.successful_koji_builds.connect(cb)
    fm_event.requested_builds.connect(fm_build)
    containeradvisory.attached_builds.connect(cb)
    module_build.components.connect(build)
    module_build.advisories.connect(advisory)

    url = '/api/v1/story/{0}/{1}'.format(resource, uid)
    rv = client.get(url)
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
                'assignee': None,
                'attached_advisories': [

                ],
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T06:43:58Z',
                'id': '5555',
                'modified_time': '2017-12-05T10:12:47Z',
                'priority': 'unspecified',
                'product_name': 'Red Hat CloudForms Management Engine',
                'product_version': '5.7.0',
                'qa_contact': None,
                'related_by_commits': [

                ],
                'reporter': None,
                'resolution': 'WORKSFORME',
                'resolved_by_commits': [

                ],
                'resource_type': 'BugzillaBug',
                'display_name': 'RHBZ#5555',
                'reverted_by_commits': [

                ],
                'severity': 'unspecified',
                'short_description': 'Fail to delete OSP tenant by CFME',
                'status': 'CLOSED',
                'target_milestone': 'GA',
                'votes': 0
            }
        ],
        'meta': {
            'story_related_nodes_forward': [0],
            'story_related_nodes_backward': [0],
            'requested_node_index': 0,
            'story_type': 'container'
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


def test_get_stories_just_artifact(client):
    """Test getting the story for a resource but only the artifact is returned."""
    Advisory.get_or_create({
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
    expected = {
        'data': [{
            'actual_ship_date': '2017-08-01T15:43:51Z',
            'advisory_name': 'RHBA-2017:2251-02',
            'assigned_to': None,
            'attached_bugs': [],
            'attached_builds': [],
            'content_types': ['docker'],
            'created_at': '2017-04-03T14:47:23Z',
            'id': '27825',
            'issue_date': '2017-08-01T05:59:34Z',
            'product_name': 'Red Hat Enterprise Linux',
            'product_short_name': 'RHEL',
            'release_date': None,
            'reporter': None,
            'resource_type': 'Advisory',
            'display_name': 'RHBA-2017:2251-02',
            'security_impact': 'None',
            'security_sla': None,
            'state': 'SHIPPED_LIVE',
            'status_time': '2017-08-01T15:43:51Z',
            'synopsis': 'cifs-utils bug fix update',
            'triggered_freshmaker_event': [],
            'update_date': '2017-08-01T07:16:00Z'
        }],
        'meta': {
            'story_related_nodes_forward': [0],
            'story_related_nodes_backward': [0],
            'requested_node_index': 0,
            'story_type': 'container'
        }
    }

    rv = client.get('/api/v1/story/advisory/27825')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_get_story_partial_story(client):
    """Test getting the story for a resource that doesn't span the whole pipeline."""
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
    cb2 = ContainerKojiBuild.get_or_create({
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '711',
        'name': 'slf4j_2',
        'release': '4.el7_4_as',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.8.4'
    })[0]

    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.successful_koji_builds.connect(cb)
    fm_event.successful_koji_builds.connect(cb2)
    expected = {
        'data': [
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'assigned_to': None,
                'attached_bugs': [],
                'attached_builds': [],
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'reporter': None,
                'resource_type': 'Advisory',
                'display_name': u'RHBA-2017:2251-02',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'triggered_freshmaker_event': [{
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                }],
                'update_date': '2017-08-01T07:16:00Z'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'display_name': 'Freshmaker event 1180',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'time_created': '2019-08-21T13:42:20Z',
                'time_done': '2099-08-21T13:42:20Z'
            },
            {
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '711',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.8.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.8.4'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [0, 0, 0],
            'story_related_nodes_backward': [0, 0, 1],
            'requested_node_index': 0,
            'story_type': 'container'
        }
    }

    rv = client.get('/api/v1/story/advisory/27825')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_get_story_fallback(client):
    """Test getting the story for a resource and falling back to a different label."""
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

    build.advisories.connect(advisory)
    expected = {
        'data': [
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': ['docker'],
                    'created_at': '2017-04-03T14:47:23Z',
                    'id': '27825',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name': 'Red Hat Enterprise Linux',
                    'product_short_name': 'RHEL',
                    'release_date': None,
                    'security_impact': 'None',
                    'security_sla': None,
                    'state': 'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51Z',
                    'synopsis': 'cifs-utils bug fix update',
                    'update_date': '2017-08-01T07:16:00Z'
                }],
                'commit': None,
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'owner': None,
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'module_builds': [],
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'tags': [],
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'display_name': 'RHBA-2017:2251-02',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'requested_node_index': 0,
            'story_related_nodes_backward': [0, 0],
            'story_related_nodes_forward': [0, 0],
            'story_type': 'container'
        }
    }

    rv = client.get('/api/v1/story/containerkojibuild/2345?fallback=kojibuild')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected
