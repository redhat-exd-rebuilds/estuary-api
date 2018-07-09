# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import pytest

from estuary.models.koji import KojiBuild, ContainerKojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit, DistGitRepo, DistGitBranch
from estuary.models.errata import Advisory, ContainerAdvisory
from estuary.models.freshmaker import FreshmakerEvent
from estuary.models.user import User


@pytest.mark.parametrize('resource,uids,expected', [
    ('bugzillabug', ['12345', '#12345', 'RHBZ#12345', 'rhbz#12345'], {
        'data': [
            {
                'assignee': None,
                'attached_advisories': [

                ],
                'classification': 'Red Hat',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'id': '12345',
                'modified_time': '2018-02-07T19:30:47+00:00',
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
                        'author_date': '2017-04-26T11:44:38+00:00',
                        'commit_date': '2017-04-26T11:44:38+00:00',
                        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                        'log_message': 'Related: #12345 - fix xyz'
                    }
                ],
                'resource_type': 'BugzillaBug',
                'reverted_by_commits': [

                ],
                'severity': 'low',
                'short_description': 'Some description',
                'status': 'VERIFIED',
                'target_milestone': 'rc',
                'votes':0
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
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 0
        }
    }),
    ('distgitcommit', ['8a63adb248ba633e200067e1ad6dc61931727bad'], {
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
                'author': None,
                'author_date': '2017-04-26T11:44:38+00:00',
                'branches': [{
                    'name': 'some-branch',
                    'repo_name': 'slf4j',
                    'repo_namespace': 'rpms'
                }],
                'children': [

                ],
                'commit_date': '2017-04-26T11:44:38+00:00',
                'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                'koji_builds': [
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
                    },
                    {
                        'classification': 'Red Hat',
                        'creation_time': '2017-04-02T06:43:58+00:00',
                        'id': '5555',
                        'modified_time': '2017-12-05T10:12:47+00:00',
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
                'reverted_bugs': [

                ]
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
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 1
        }
    }),
    ('kojibuild', ['2345', 'slf4j-1.7.4-4.el7_4', 'slf4j-1.7.4-4.el7_4.src.rpm'], {
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
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51+00:00',
                        'advisory_name': 'RHBA-2017:2251-02',
                        'content_types': [
                            'docker'
                        ],
                        'created_at': '2017-04-03T14:47:23+00:00',
                        'id': '27825',
                        'issue_date': '2017-08-01T05:59:34+00:00',
                        'product_name': 'Red Hat Enterprise Linux',
                        'product_short_name': 'RHEL',
                        'release_date': None,
                        'security_impact': 'None',
                        'security_sla': None,
                        'state': 'SHIPPED_LIVE',
                        'status_time': '2017-08-01T15:43:51+00:00',
                        'synopsis': 'cifs-utils bug fix update',
                        'type': 'RHBA',
                        'update_date': '2017-08-01T07:16:00+00:00',
                        'updated_at': '2017-08-01T15:43:51+00:00'
                    }
                ],
                'commit':{
                    'author_date': '2017-04-26T11:44:38+00:00',
                    'commit_date': '2017-04-26T11:44:38+00:00',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz'
                },
                'completion_time': '2017-04-02T19:39:06+00:00',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'owner': None,
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06+00:00',
                'state': 1,
                'tags': [

                ],
                'tasks': [

                ],
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': [
                    'docker'
                ],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 2
        }
    }),
    ('advisory', ['27825', 'RHBA-2017:2251-02', 'RHBA-2017:2251'], {
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
                'assigned_to': None,
                'attached_bugs': [

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
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'package_owner': None,
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'reporter': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'states': [

                ],
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'triggered_freshmaker_event': [
                    {
                        'event_type_id': 8,
                        'id': '1180',
                        'message_id': 'ID:messaging-devops-broker01.test',
                        'state': 2,
                        'state_name': 'COMPLETE',
                        'state_reason': 'All container images have been rebuilt.',
                        'url': '/api/1/events/1180'
                    }
                ],
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 3
        }
    }),
    ('freshmakerevent', ['1180'], {
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
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            },
            {
                'event_type_id': 8,
                'id': '1180',
                'message_id': 'ID:messaging-devops-broker01.test',
                'resource_type': 'FreshmakerEvent',
                'state': 2,
                'state_name': 'COMPLETE',
                'state_reason': 'All container images have been rebuilt.',
                'triggered_by_advisory': {
                    'actual_ship_date': '2017-08-01T15:43:51+00:00',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2017-04-03T14:47:23+00:00',
                    'id': '27825',
                    'issue_date': '2017-08-01T05:59:34+00:00',
                    'product_name': 'Red Hat Enterprise Linux',
                    'product_short_name': 'RHEL',
                    'release_date': None,
                    'security_impact': 'None',
                    'security_sla': None,
                    'state': 'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51+00:00',
                    'synopsis': 'cifs-utils bug fix update',
                    'type': 'RHBA',
                    'update_date': '2017-08-01T07:16:00+00:00',
                    'updated_at': '2017-08-01T15:43:51+00:00'
                },
                'triggered_container_builds': [
                    {
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
                        'version': '1.7.4'
                    }
                ],
                'url': '/api/1/events/1180'
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'ContainerAdvisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0],
            'requested_node_index': 4
        }
    }),
    ('containerkojibuild', ['710'], {
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
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51+00:00',
                        'advisory_name': 'RHBA-2017:2251-03',
                        'content_types': [
                            'docker'
                        ],
                        'created_at':'2017-04-03T14:47:23+00:00',
                        'id':'12327',
                        'issue_date':'2017-08-01T05:59:34+00:00',
                        'product_name':'Red Hat Enterprise Linux',
                        'product_short_name':'RHEL',
                        'release_date':None,
                        'security_impact':'None',
                        'security_sla':None,
                        'state':'SHIPPED_LIVE',
                        'status_time':'2017-08-01T15:43:51+00:00',
                        'synopsis':'cifs-utils bug fix update',
                        'type':'RHBA',
                        'update_date':'2017-08-01T07:16:00+00:00',
                        'updated_at':'2017-08-01T15:43:51+00:00'
                    }
                ],
                'commit':None,
                'completion_time':'2017-04-02T19:39:06+00:00',
                'creation_time':'2017-04-02T19:39:06+00:00',
                'epoch':'0',
                'extra':None,
                'id':'710',
                'name':'slf4j_2',
                'original_nvr':None,
                'owner':None,
                'release':'4.el7_4_as',
                'resource_type':'ContainerKojiBuild',
                'start_time':'2017-04-02T19:39:06+00:00',
                'state':1,
                'tags':[

                ],
                'tasks':[

                ],
                'triggered_by_freshmaker_event':{
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'url': '/api/1/events/1180'
                },
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'content_types': [
                    'docker'
                ],
                'created_at':'2017-04-03T14:47:23+00:00',
                'id':'12327',
                'issue_date':'2017-08-01T05:59:34+00:00',
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'resource_type':'ContainerAdvisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'status_time':'2017-08-01T15:43:51+00:00',
                'synopsis':'cifs-utils bug fix update',
                'type':'RHBA',
                'update_date':'2017-08-01T07:16:00+00:00',
                'updated_at':'2017-08-01T15:43:51+00:00'
            }
        ],
        'meta':{
            'requested_node_index': 5,
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0]
        }
    }),
    ('containeradvisory', ['12327'], {
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
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-03',
                'assigned_to': None,
                'attached_bugs': [

                ],
                'attached_builds':[
                    {
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
                        'version': '1.7.4'
                    }
                ],
                'content_types': [
                    'docker'
                ],
                'created_at':'2017-04-03T14:47:23+00:00',
                'id':'12327',
                'issue_date':'2017-08-01T05:59:34+00:00',
                'package_owner':None,
                'product_name':'Red Hat Enterprise Linux',
                'product_short_name':'RHEL',
                'release_date':None,
                'reporter':None,
                'resource_type':'ContainerAdvisory',
                'security_impact':'None',
                'security_sla':None,
                'state':'SHIPPED_LIVE',
                'states':[

                ],
                'status_time':'2017-08-01T15:43:51+00:00',
                'synopsis':'cifs-utils bug fix update',
                'triggered_freshmaker_event':[

                ],
                'type':'RHBA',
                'update_date':'2017-08-01T07:16:00+00:00',
                'updated_at':'2017-08-01T15:43:51+00:00'
            }
        ],
        'meta':{
            'requested_node_index': 6,
            'story_related_nodes_forward': [1, 0, 0, 0, 0, 0, 0],
            'story_related_nodes_backward': [0, 0, 0, 0, 0, 0, 0]
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
        'type_': 'RHBA',
        'update_date': datetime(2017, 8, 1, 7, 16),
        'updated_at': datetime(2017, 8, 1, 15, 43, 51)
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
    fm_event.triggered_container_builds.connect(cb)
    containeradvisory.attached_builds.connect(cb)

    for uid in uids:
        url = '/api/v1/story/{0}/{1}'.format(resource, uid)
        rv = client.get(url)
        assert rv.status_code == 200, 'Failed getting the resource at: {0}'.format(url)
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
                'creation_time': '2017-04-02T06:43:58+00:00',
                'id': '5555',
                'modified_time': '2017-12-05T10:12:47+00:00',
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
                'reverted_by_commits': [

                ],
                'severity': 'unspecified',
                'short_description': 'Fail to delete OSP tenant by CFME',
                'status': 'CLOSED',
                'target_milestone': 'GA',
                'votes':0
            }
        ],
        'meta': {
            'story_related_nodes_forward': [0],
            'story_related_nodes_backward': [0],
            'requested_node_index': 0
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
        'type_': 'RHBA',
        'update_date': datetime(2017, 8, 1, 7, 16),
        'updated_at': datetime(2017, 8, 1, 15, 43, 51)
    })[0]
    expected = {
        'data': [{
            'actual_ship_date': '2017-08-01T15:43:51+00:00',
            'advisory_name': 'RHBA-2017:2251-02',
            'assigned_to': None,
            'attached_bugs': [],
            'attached_builds': [],
            'content_types': ['docker'],
            'created_at': '2017-04-03T14:47:23+00:00',
            'id': '27825',
            'issue_date': '2017-08-01T05:59:34+00:00',
            'package_owner': None,
            'product_name': 'Red Hat Enterprise Linux',
            'product_short_name': 'RHEL',
            'release_date': None,
            'reporter': None,
            'resource_type': 'Advisory',
            'security_impact': 'None',
            'security_sla': None,
            'state': 'SHIPPED_LIVE',
            'states': [],
            'status_time': '2017-08-01T15:43:51+00:00',
            'synopsis': 'cifs-utils bug fix update',
            'triggered_freshmaker_event': [],
            'type': 'RHBA',
            'update_date': '2017-08-01T07:16:00+00:00',
            'updated_at': '2017-08-01T15:43:51+00:00'
        }],
        'meta': {
            'story_related_nodes_forward': [0],
            'story_related_nodes_backward': [0],
            'requested_node_index': 0
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
    fm_event.triggered_container_builds.connect(cb)
    fm_event.triggered_container_builds.connect(cb2)
    expected = {
        'data': [
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-02',
                'assigned_to': None,
                'attached_bugs': [],
                'attached_builds': [],
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'package_owner': None,
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'reporter': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'states': [],
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'triggered_freshmaker_event': [{
                    'event_type_id': 8,
                    'id': '1180',
                    'message_id': 'ID:messaging-devops-broker01.test',
                    'state': 2,
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'url': '/api/1/events/1180'
                }],
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
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
                'completion_time': '2017-04-02T19:39:06+00:00',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'epoch': '0',
                'extra': None,
                'id': '711',
                'name': 'slf4j_2',
                'original_nvr': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'start_time': '2017-04-02T19:39:06+00:00',
                'state': 1,
                'version': '1.8.4'
            }
        ],
        'meta': {
            'story_related_nodes_forward': [0, 0, 0],
            'story_related_nodes_backward': [0, 0, 1],
            'requested_node_index': 0
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
        'type_': 'RHBA',
        'update_date': datetime(2017, 8, 1, 7, 16),
        'updated_at': datetime(2017, 8, 1, 15, 43, 51)
    })[0]

    build.advisories.connect(advisory)
    expected = {
        'data': [
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51+00:00',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': ['docker'],
                    'created_at': '2017-04-03T14:47:23+00:00',
                    'id': '27825',
                    'issue_date': '2017-08-01T05:59:34+00:00',
                    'product_name': 'Red Hat Enterprise Linux',
                    'product_short_name': 'RHEL',
                    'release_date': None,
                    'security_impact': 'None',
                    'security_sla': None,
                    'state': 'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51+00:00',
                    'synopsis': 'cifs-utils bug fix update',
                    'type': 'RHBA',
                    'update_date': '2017-08-01T07:16:00+00:00',
                    'updated_at': '2017-08-01T15:43:51+00:00'
                }],
                'commit': None,
                'completion_time': '2017-04-02T19:39:06+00:00',
                'creation_time': '2017-04-02T19:39:06+00:00',
                'epoch': '0',
                'extra': None,
                'id': '2345',
                'name': 'slf4j',
                'owner': None,
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06+00:00',
                'state': 1,
                'tags': [],
                'tasks': [],
                'version': '1.7.4'
            },
            {
                'actual_ship_date': '2017-08-01T15:43:51+00:00',
                'advisory_name': 'RHBA-2017:2251-02',
                'content_types': ['docker'],
                'created_at': '2017-04-03T14:47:23+00:00',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34+00:00',
                'product_name': 'Red Hat Enterprise Linux',
                'product_short_name': 'RHEL',
                'release_date': None,
                'resource_type': 'Advisory',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51+00:00',
                'synopsis': 'cifs-utils bug fix update',
                'type': 'RHBA',
                'update_date': '2017-08-01T07:16:00+00:00',
                'updated_at': '2017-08-01T15:43:51+00:00'
            }
        ],
        'meta': {
            'requested_node_index': 0,
            'story_related_nodes_backward': [0, 0],
            'story_related_nodes_forward': [0, 0]
        }
    }

    rv = client.get('/api/v1/story/containerkojibuild/2345?fallback=kojibuild')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected
