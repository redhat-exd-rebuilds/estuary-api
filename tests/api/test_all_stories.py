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


@pytest.mark.parametrize('resource,uid,expected', [
    ('bugzillabug', '12345', [
        {
            'data': [
                {
                    'assignee': None,
                    'attached_advisories': [

                    ],
                    'classification':'Red Hat',
                    'creation_time': '2017-04-02T19:39:06Z',
                    'display_name':'RHBZ#12345',
                    'id':'12345',
                    'modified_time': '2018-02-07T19:30:47Z',
                    'priority':'high',
                    'product_name':'Red Hat Enterprise Linux',
                    'product_version':'7.5',
                    'qa_contact':None,
                    'related_by_commits':[

                    ],
                    'reporter':None,
                    'resolution':'',
                    'resolved_by_commits':[
                        {
                            'author_date': '2017-04-26T11:44:38Z',
                            'commit_date': '2018-05-02T10:36:47Z',
                            'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                            'log_message': 'Related: #12345 - fix xyz',
                            'resource_type': 'DistGitCommit',
                            'display_name': 'commit #8a63adb',
                        }
                    ],
                    'resource_type': 'BugzillaBug',
                    'reverted_by_commits': [

                    ],
                    'severity':'low',
                    'short_description':'Some description',
                    'status':'VERIFIED',
                    'target_milestone':'rc',
                    'timeline_timestamp': '2017-04-02T19:39:06Z',
                    'votes':0
                },
                {
                    'author_date': '2017-04-26T11:44:38Z',
                    'commit_date': '2018-05-02T10:36:47Z',
                    'display_name': 'commit #8a63adb',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz',
                    'resource_type': 'DistGitCommit',
                    'timeline_timestamp': '2018-05-02T10:36:47Z'
                },
                {
                    'completion_time': '2018-06-02T10:55:47Z',
                    'creation_time': '2018-06-02T10:36:47Z',
                    'display_name': 'slf4j-1.7.4-4.el7_4',
                    'epoch': '0',
                    'extra': None,
                    'id': '2345',
                    'name': 'slf4j',
                    'release': '4.el7_4',
                    'resource_type': 'KojiBuild',
                    'start_time': '2018-06-02T10:36:47Z',
                    'state': 1,
                    'timeline_timestamp': '2018-06-02T10:36:47Z',
                    'version': '1.7.4'
                },
                {
                    'actual_ship_date': None,
                    'advisory_name': 'RHBA-2017:27760-01',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2018-04-21T19:36:47Z',
                    'display_name':'RHBA-2017:27760-01',
                    'id':'123456',
                    'issue_date': '2018-03-14T05:53:25Z',
                    'product_name':'Release End2End Test',
                    'product_short_name':'release-e2e-test',
                    'release_date':None,
                    'resource_type':'Advisory',
                    'security_impact':'None',
                    'security_sla':None,
                    'state':'DROPPED_NO_SHIP',
                    'status_time': '2018-03-14T07:53:25Z',
                    'synopsis':'This is a synopsis of a test advisory.',
                    'update_date': '2018-04-21T19:36:47Z',
                    'timeline_timestamp': '2018-04-21T19:36:47Z'
                }
            ],
            'meta':{
                'story_related_nodes_backward': [0, 0, 0, 1],
                'story_related_nodes_forward': [0, 1, 0, 0],
                'total_lead_time': 29852059.0,
                'total_processing_time': 1140.0,
                'processing_time_flag': False,
                'total_wait_time': 36773861.0,
                'wait_times': [34095461.0, 2678400.0, None],
                'requested_node_index': 0,
                'story_type': 'container'
            }
        },
        {
            'data': [
                {
                    'assignee': None,
                    'attached_advisories': [

                    ],
                    'classification':'Red Hat',
                    'creation_time': '2017-04-02T19:39:06Z',
                    'display_name':'RHBZ#12345',
                    'id':'12345',
                    'modified_time': '2018-02-07T19:30:47Z',
                    'priority':'high',
                    'product_name':'Red Hat Enterprise Linux',
                    'product_version':'7.5',
                    'qa_contact':None,
                    'related_by_commits':[

                    ],
                    'reporter':None,
                    'resolution':'',
                    'resolved_by_commits':[
                        {
                            'author_date': '2017-04-26T11:44:38Z',
                            'commit_date': '2018-05-02T10:36:47Z',
                            'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                            'log_message': 'Related: #12345 - fix xyz',
                            'resource_type': 'DistGitCommit',
                            'display_name': 'commit #8a63adb',
                        }
                    ],
                    'resource_type': 'BugzillaBug',
                    'reverted_by_commits': [

                    ],
                    'severity':'low',
                    'short_description':'Some description',
                    'status':'VERIFIED',
                    'target_milestone':'rc',
                    'timeline_timestamp': '2017-04-02T19:39:06Z',
                    'votes':0
                },
                {
                    'author_date': '2017-04-26T11:44:38Z',
                    'commit_date': '2018-05-02T10:36:47Z',
                    'display_name': 'commit #8a63adb',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz',
                    'resource_type': 'DistGitCommit',
                    'timeline_timestamp': '2018-05-02T10:36:47Z'
                },
                {
                    'completion_time': '2018-06-02T10:55:47Z',
                    'creation_time': '2018-06-02T10:36:47Z',
                    'display_name': 'slf4j-1.7.4-4.el7_4',
                    'epoch': '0',
                    'extra': None,
                    'id': '2345',
                    'name': 'slf4j',
                    'release': '4.el7_4',
                    'resource_type': 'KojiBuild',
                    'start_time': '2018-06-02T10:36:47Z',
                    'state': 1,
                    'timeline_timestamp': '2018-06-02T10:36:47Z',
                    'version': '1.7.4'
                },
                {
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2018-06-13T10:36:47Z',
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
                    'update_date': '2017-08-01T07:16:00Z',
                    'timeline_timestamp': '2018-06-13T10:36:47Z'
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
                    'time_created': '2018-08-13T10:36:47Z',
                    'time_done': '2018-08-13T12:45:47Z',
                    'timeline_timestamp': '2018-08-13T10:36:47Z'
                },
                {
                    'completion_time': '2018-08-17T13:55:47Z',
                    'creation_time': '2018-08-17T08:32:47Z',
                    'display_name': 'some_build-1.7.5-4.el7_4_as',
                    'epoch': '0',
                    'extra': None,
                    'id': '811',
                    'name': 'some_build',
                    'original_nvr': None,
                    'release': '4.el7_4_as',
                    'resource_type': 'ContainerKojiBuild',
                    'start_time': '2018-08-17T08:32:47Z',
                    'state': 2,
                    'timeline_timestamp': '2018-08-17T08:32:47Z',
                    'version': '1.7.5'
                }
            ],
            'meta': {
                'story_related_nodes_backward': [0, 0, 0, 1, 0, 1],
                'story_related_nodes_forward': [0, 1, 0, 0, 0, 0],
                'total_lead_time': 43352201.0,
                'total_processing_time': 358680.0,
                'processing_time_flag': False,
                'total_wait_time': 70277497.0,
                'wait_times': [34095461.0, 2678400.0, 949260.0, 32554376.0, 338160.0],
                'requested_node_index': 0,
                'story_type': 'container'
            }
        }
    ]),
    ('kojibuild', '2345', [
        {
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
                    'timeline_timestamp': '2017-04-02T19:39:06Z',
                    'votes': 0
                },
                {
                    'author_date': '2017-04-26T11:44:38Z',
                    'commit_date': '2018-05-02T10:36:47Z',
                    'display_name': 'commit #8a63adb',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz',
                    'resource_type': 'DistGitCommit',
                    'timeline_timestamp': '2018-05-02T10:36:47Z',
                },
                {
                    'advisories': [
                        {
                            'actual_ship_date': None,
                            'advisory_name': 'RHBA-2017:27760-01',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-04-21T19:36:47Z',
                            'display_name': 'RHBA-2017:27760-01',
                            'id':'123456',
                            'issue_date': '2018-03-14T05:53:25Z',
                            'product_name':'Release End2End Test',
                            'product_short_name':'release-e2e-test',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'DROPPED_NO_SHIP',
                            'status_time': '2018-03-14T07:53:25Z',
                            'synopsis':'This is a synopsis of a test advisory.',
                            'update_date': '2018-04-21T19:36:47Z'
                        },
                        {
                            'actual_ship_date': '2017-08-01T15:43:51Z',
                            'advisory_name': 'RHBA-2017:2251-02',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-06-13T10:36:47Z',
                            'display_name': 'RHBA-2017:2251-02',
                            'id':'27825',
                            'issue_date': '2017-08-01T05:59:34Z',
                            'product_name':'Red Hat Enterprise Linux',
                            'product_short_name':'RHEL',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'SHIPPED_LIVE',
                            'status_time': '2017-08-01T15:43:51Z',
                            'synopsis':'cifs-utils bug fix update',
                            'update_date': '2017-08-01T07:16:00Z'
                        }
                    ],
                    'commit':{
                        'author_date': '2017-04-26T11:44:38Z',
                        'commit_date': '2018-05-02T10:36:47Z',
                        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                        'log_message': 'Related: #12345 - fix xyz',
                        'resource_type': 'DistGitCommit',
                        'display_name': 'commit #8a63adb',
                    },
                    'completion_time': '2018-06-02T10:55:47Z',
                    'creation_time': '2018-06-02T10:36:47Z',
                    'display_name': 'slf4j-1.7.4-4.el7_4',
                    'epoch': '0',
                    'extra': None,
                    'id': '2345',
                    'module_builds': [

                    ],
                    'name':'slf4j',
                    'owner':None,
                    'release':'4.el7_4',
                    'resource_type':'KojiBuild',
                    'start_time': '2018-06-02T10:36:47Z',
                    'state':1,
                    'tags':[

                    ],
                    'timeline_timestamp': '2018-06-02T10:36:47Z',
                    'version':'1.7.4'
                },
                {
                    'actual_ship_date': None,
                    'advisory_name': 'RHBA-2017:27760-01',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2018-04-21T19:36:47Z',
                    'display_name':'RHBA-2017:27760-01',
                    'id':'123456',
                    'issue_date': '2018-03-14T05:53:25Z',
                    'product_name':'Release End2End Test',
                    'product_short_name':'release-e2e-test',
                    'release_date':None,
                    'resource_type':'Advisory',
                    'security_impact':'None',
                    'security_sla':None,
                    'state':'DROPPED_NO_SHIP',
                    'status_time': '2018-03-14T07:53:25Z',
                    'synopsis':'This is a synopsis of a test advisory.',
                    'update_date': '2018-04-21T19:36:47Z',
                    'timeline_timestamp': '2018-04-21T19:36:47Z'
                }
            ],
            'meta':{
                'requested_node_index': 2,
                'story_related_nodes_backward': [0, 0, 0, 1],
                'story_related_nodes_forward': [0, 1, 0, 0],
                'total_lead_time': 29852059.0,
                'total_processing_time': 1140.0,
                'processing_time_flag': False,
                'total_wait_time': 36773861.0,
                'wait_times': [34095461.0, 2678400.0, None],
                'story_type': 'container'
            }
        },
        {
            'data': [
                {
                    'classification': 'Red Hat',
                    'creation_time': '2017-04-01T17:41:04Z',
                    'display_name': 'RHBZ#1245',
                    'id': '1245',
                    'modified_time': '2018-03-14T05:53:19Z',
                    'priority': 'unspecified',
                    'product_name': 'Red Hat Enterprise Linux 7',
                    'product_version': '7.2',
                    'resolution': 'DUPLICATE',
                    'resource_type': 'BugzillaBug',
                    'severity': 'medium',
                    'short_description': 'some description',
                    'status': 'CLOSED',
                    'target_milestone': 'rc',
                    'timeline_timestamp': '2017-04-01T17:41:04Z',
                    'votes': 0
                },
                {
                    'author_date': '2018-03-14T05:53:25Z',
                    'commit_date': '2018-03-14T05:52:19Z',
                    'display_name': 'commit #f4dfc64',
                    'hash': 'f4dfc64c10a90492303e4f14ad3549a1a2b13575',
                    'log_message': 'Repo creation',
                    'resource_type': 'DistGitCommit',
                    'timeline_timestamp': '2018-03-14T05:52:19Z'
                },
                {
                    'advisories': [
                        {
                            'actual_ship_date': None,
                            'advisory_name': 'RHBA-2017:27760-01',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-04-21T19:36:47Z',
                            'display_name': 'RHBA-2017:27760-01',
                            'id':'123456',
                            'issue_date': '2018-03-14T05:53:25Z',
                            'product_name':'Release End2End Test',
                            'product_short_name':'release-e2e-test',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'DROPPED_NO_SHIP',
                            'status_time': '2018-03-14T07:53:25Z',
                            'synopsis':'This is a synopsis of a test advisory.',
                            'update_date': '2018-04-21T19:36:47Z'
                        },
                        {
                            'actual_ship_date': '2017-08-01T15:43:51Z',
                            'advisory_name': 'RHBA-2017:2251-02',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-06-13T10:36:47Z',
                            'display_name': 'RHBA-2017:2251-02',
                            'id': '27825',
                            'issue_date': '2017-08-01T05:59:34Z',
                            'product_name':'Red Hat Enterprise Linux',
                            'product_short_name':'RHEL',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'SHIPPED_LIVE',
                            'status_time': '2017-08-01T15:43:51Z',
                            'synopsis':'cifs-utils bug fix update',
                            'update_date': '2017-08-01T07:16:00Z'
                        }
                    ],
                    'commit':{
                        'author_date': '2017-04-26T11:44:38Z',
                        'commit_date': '2018-05-02T10:36:47Z',
                        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                        'log_message': 'Related: #12345 - fix xyz',
                        'display_name': 'commit #8a63adb',
                        'resource_type': 'DistGitCommit',
                    },
                    'completion_time': '2018-06-02T10:55:47Z',
                    'creation_time': '2018-06-02T10:36:47Z',
                    'display_name': 'slf4j-1.7.4-4.el7_4',
                    'epoch': '0',
                    'extra': None,
                    'id': '2345',
                    'module_builds': [

                    ],
                    'name':'slf4j',
                    'owner':None,
                    'release':'4.el7_4',
                    'resource_type':'KojiBuild',
                    'start_time': '2018-06-02T10:36:47Z',
                    'state':1,
                    'tags':[

                    ],
                    'timeline_timestamp': '2018-06-02T10:36:47Z',
                    'version':'1.7.4'
                },
                {
                    'actual_ship_date': None,
                    'advisory_name': 'RHBA-2017:27760-01',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2018-04-21T19:36:47Z',
                    'display_name':'RHBA-2017:27760-01',
                    'id':'123456',
                    'issue_date': '2018-03-14T05:53:25Z',
                    'product_name':'Release End2End Test',
                    'product_short_name':'release-e2e-test',
                    'release_date':None,
                    'resource_type':'Advisory',
                    'security_impact':'None',
                    'security_sla':None,
                    'state':'DROPPED_NO_SHIP',
                    'status_time': '2018-03-14T07:53:25Z',
                    'synopsis':'This is a synopsis of a test advisory.',
                    'update_date': '2018-04-21T19:36:47Z',
                    'timeline_timestamp': '2018-04-21T19:36:47Z'
                }
            ],
            'meta':{
                'requested_node_index': 2,
                'story_related_nodes_backward': [0, 0, 0, 1],
                'story_related_nodes_forward': [0, 1, 0, 0],
                'total_lead_time': 29945541.0,
                'total_processing_time': 1140.0,
                'processing_time_flag': False,
                'total_wait_time': 36867343.0,
                'wait_times': [29938275.0, 6929068.0, None],
                'story_type': 'container'
            }
        },
        {
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
                    'timeline_timestamp': '2017-04-02T19:39:06Z',
                    'votes': 0
                },
                {
                    'author_date': '2017-04-26T11:44:38Z',
                    'commit_date': '2018-05-02T10:36:47Z',
                    'display_name': 'commit #8a63adb',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz',
                    'resource_type': 'DistGitCommit',
                    'timeline_timestamp': '2018-05-02T10:36:47Z'
                },
                {
                    'advisories': [
                        {
                            'actual_ship_date': None,
                            'advisory_name': 'RHBA-2017:27760-01',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-04-21T19:36:47Z',
                            'display_name': 'RHBA-2017:27760-01',
                            'id':'123456',
                            'issue_date': '2018-03-14T05:53:25Z',
                            'product_name':'Release End2End Test',
                            'product_short_name':'release-e2e-test',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'DROPPED_NO_SHIP',
                            'status_time': '2018-03-14T07:53:25Z',
                            'synopsis':'This is a synopsis of a test advisory.',
                            'update_date': '2018-04-21T19:36:47Z'
                        },
                        {
                            'actual_ship_date': '2017-08-01T15:43:51Z',
                            'advisory_name': 'RHBA-2017:2251-02',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-06-13T10:36:47Z',
                            'display_name': 'RHBA-2017:2251-02',
                            'id':'27825',
                            'issue_date': '2017-08-01T05:59:34Z',
                            'product_name':'Red Hat Enterprise Linux',
                            'product_short_name':'RHEL',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'SHIPPED_LIVE',
                            'status_time': '2017-08-01T15:43:51Z',
                            'synopsis':'cifs-utils bug fix update',
                            'update_date': '2017-08-01T07:16:00Z'
                        }
                    ],
                    'commit':{
                        'author_date': '2017-04-26T11:44:38Z',
                        'commit_date': '2018-05-02T10:36:47Z',
                        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                        'log_message': 'Related: #12345 - fix xyz',
                        'display_name': 'commit #8a63adb',
                        'resource_type': 'DistGitCommit',
                    },
                    'completion_time': '2018-06-02T10:55:47Z',
                    'creation_time': '2018-06-02T10:36:47Z',
                    'display_name': 'slf4j-1.7.4-4.el7_4',
                    'epoch': '0',
                    'extra': None,
                    'id': '2345',
                    'module_builds': [

                    ],
                    'name':'slf4j',
                    'owner':None,
                    'release':'4.el7_4',
                    'resource_type':'KojiBuild',
                    'start_time': '2018-06-02T10:36:47Z',
                    'state':1,
                    'tags':[

                    ],
                    'timeline_timestamp': '2018-06-02T10:36:47Z',
                    'version':'1.7.4'
                },
                {
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2018-06-13T10:36:47Z',
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
                    'update_date': '2017-08-01T07:16:00Z',
                    'timeline_timestamp': '2018-06-13T10:36:47Z'
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
                    'time_created': '2018-08-13T10:36:47Z',
                    'time_done': '2018-08-13T12:45:47Z',
                    'timeline_timestamp': '2018-08-13T10:36:47Z'
                },
                {
                    'completion_time': '2018-08-17T13:55:47Z',
                    'creation_time': '2018-08-17T08:32:47Z',
                    'display_name': 'some_build-1.7.5-4.el7_4_as',
                    'epoch': '0',
                    'extra': None,
                    'id': '811',
                    'name': 'some_build',
                    'original_nvr': None,
                    'release': '4.el7_4_as',
                    'resource_type': 'ContainerKojiBuild',
                    'start_time': '2018-08-17T08:32:47Z',
                    'state': 2,
                    'timeline_timestamp': '2018-08-17T08:32:47Z',
                    'version': '1.7.5'
                }
            ],
            'meta': {
                'requested_node_index': 2,
                'story_related_nodes_backward': [0, 0, 0, 1, 0, 1],
                'story_related_nodes_forward': [0, 1, 0, 0, 0, 0],
                'total_lead_time': 43352201.0,
                'total_processing_time': 358680.0,
                'processing_time_flag': False,
                'total_wait_time': 70277497.0,
                'wait_times': [34095461.0, 2678400.0, 949260.0, 32554376.0, 338160.0],
                'story_type': 'container'
            }
        },
        {
            'data': [
                {
                    'classification': 'Red Hat',
                    'creation_time': '2017-04-01T17:41:04Z',
                    'display_name': 'RHBZ#1245',
                    'id': '1245',
                    'modified_time': '2018-03-14T05:53:19Z',
                    'priority': 'unspecified',
                    'product_name': 'Red Hat Enterprise Linux 7',
                    'product_version': '7.2',
                    'resolution': 'DUPLICATE',
                    'resource_type': 'BugzillaBug',
                    'severity': 'medium',
                    'short_description': 'some description',
                    'status': 'CLOSED',
                    'target_milestone': 'rc',
                    'timeline_timestamp': '2017-04-01T17:41:04Z',
                    'votes': 0
                },
                {
                    'author_date': '2018-03-14T05:53:25Z',
                    'commit_date': '2018-03-14T05:52:19Z',
                    'display_name': 'commit #f4dfc64',
                    'hash': 'f4dfc64c10a90492303e4f14ad3549a1a2b13575',
                    'log_message': 'Repo creation',
                    'resource_type': 'DistGitCommit',
                    'timeline_timestamp': '2018-03-14T05:52:19Z'
                },
                {
                    'advisories': [
                        {
                            'actual_ship_date': None,
                            'advisory_name': 'RHBA-2017:27760-01',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-04-21T19:36:47Z',
                            'display_name': 'RHBA-2017:27760-01',
                            'id':'123456',
                            'issue_date': '2018-03-14T05:53:25Z',
                            'product_name':'Release End2End Test',
                            'product_short_name':'release-e2e-test',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'DROPPED_NO_SHIP',
                            'status_time': '2018-03-14T07:53:25Z',
                            'synopsis':'This is a synopsis of a test advisory.',
                            'update_date': '2018-04-21T19:36:47Z'
                        },
                        {
                            'actual_ship_date': '2017-08-01T15:43:51Z',
                            'advisory_name': 'RHBA-2017:2251-02',
                            'content_types': [
                                'docker'
                            ],
                            'created_at': '2018-06-13T10:36:47Z',
                            'display_name': 'RHBA-2017:2251-02',
                            'id':'27825',
                            'issue_date': '2017-08-01T05:59:34Z',
                            'product_name':'Red Hat Enterprise Linux',
                            'product_short_name':'RHEL',
                            'release_date':None,
                            'resource_type': 'Advisory',
                            'security_impact':'None',
                            'security_sla':None,
                            'state':'SHIPPED_LIVE',
                            'status_time': '2017-08-01T15:43:51Z',
                            'synopsis':'cifs-utils bug fix update',
                            'update_date': '2017-08-01T07:16:00Z'
                        }
                    ],
                    'commit':{
                        'author_date': '2017-04-26T11:44:38Z',
                        'commit_date': '2018-05-02T10:36:47Z',
                        'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                        'log_message': 'Related: #12345 - fix xyz',
                        'display_name': 'commit #8a63adb',
                        'resource_type': 'DistGitCommit'
                    },
                    'completion_time': '2018-06-02T10:55:47Z',
                    'creation_time': '2018-06-02T10:36:47Z',
                    'display_name': 'slf4j-1.7.4-4.el7_4',
                    'epoch': '0',
                    'extra': None,
                    'id': '2345',
                    'module_builds': [

                    ],
                    'name':'slf4j',
                    'owner':None,
                    'release':'4.el7_4',
                    'resource_type':'KojiBuild',
                    'start_time': '2018-06-02T10:36:47Z',
                    'state':1,
                    'tags':[

                    ],
                    'timeline_timestamp': '2018-06-02T10:36:47Z',
                    'version':'1.7.4'
                },
                {
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': [
                        'docker'
                    ],
                    'created_at': '2018-06-13T10:36:47Z',
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
                    'update_date': '2017-08-01T07:16:00Z',
                    'timeline_timestamp': '2018-06-13T10:36:47Z'
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
                    'time_created': '2018-08-13T10:36:47Z',
                    'time_done': '2018-08-13T12:45:47Z',
                    'timeline_timestamp': '2018-08-13T10:36:47Z'
                },
                {
                    'completion_time': '2018-08-17T13:55:47Z',
                    'creation_time': '2018-08-17T08:32:47Z',
                    'display_name': 'some_build-1.7.5-4.el7_4_as',
                    'epoch': '0',
                    'extra': None,
                    'id': '811',
                    'name': 'some_build',
                    'original_nvr': None,
                    'release': '4.el7_4_as',
                    'resource_type': 'ContainerKojiBuild',
                    'start_time': '2018-08-17T08:32:47Z',
                    'state': 2,
                    'timeline_timestamp': '2018-08-17T08:32:47Z',
                    'version': '1.7.5'
                }
            ],
            'meta': {
                'requested_node_index': 2,
                'story_related_nodes_backward': [0, 0, 0, 1, 0, 1],
                'story_related_nodes_forward':[0, 1, 0, 0, 0, 0],
                'total_lead_time': 43445683.0,
                'total_processing_time': 358680.0,
                'processing_time_flag': False,
                'total_wait_time': 70370979.0,
                'wait_times': [29938275.0, 6929068.0, 949260.0, 32554376.0, 338160.0],
                'story_type': 'container'
            }
        }
    ])

])
def test_all_stories(client, resource, uid, expected):
    """Test getting all unique stories for an artifact."""
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
        'creation_time': datetime(2017, 4, 1, 17, 41, 4),
        'severity': 'medium',
        'short_description': 'some description',
        'product_version': '7.2',
        'classification': 'Red Hat',
        'priority': 'unspecified',
        'product_name': 'Red Hat Enterprise Linux 7',
        'resolution': 'DUPLICATE',
        'target_milestone': 'rc',
        'modified_time': datetime(2018, 3, 14, 5, 53, 19),
        'votes': 0,
        'id_': '1245',
        'status': 'CLOSED'
    })[0]
    commit = DistGitCommit.get_or_create({
        'author_date': datetime(2017, 4, 26, 11, 44, 38),
        'commit_date': datetime(2018, 5, 2, 10, 36, 47),
        'hash_': '8a63adb248ba633e200067e1ad6dc61931727bad',
        'log_message': 'Related: #12345 - fix xyz'
    })[0]
    commit_two = DistGitCommit.get_or_create({
        'commit_date': datetime(2018, 3, 14, 5, 52, 19),
        'author_date': datetime(2018, 3, 14, 5, 53, 25),
        'log_message': 'Repo creation',
        'hash_': 'f4dfc64c10a90492303e4f14ad3549a1a2b13575'
    })[0]
    build = KojiBuild.get_or_create({
        'completion_time': datetime(2018, 6, 2, 10, 55, 47),
        'creation_time': datetime(2018, 6, 2, 10, 36, 47),
        'epoch': '0',
        'id_': '2345',
        'name': 'slf4j',
        'release': '4.el7_4',
        'start_time': datetime(2018, 6, 2, 10, 36, 47),
        'state': 1,
        'version': '1.7.4'
    })[0]
    advisory = Advisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-02',
        'content_types': ['docker'],
        'created_at': datetime(2018, 6, 13, 10, 36, 47),
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
    advisory_two = Advisory.get_or_create({
        'security_impact': 'None',
        'created_at': datetime(2018, 4, 21, 19, 36, 47),
        'synopsis': 'This is a synopsis of a test advisory.',
        'product_name': 'Release End2End Test',
        'update_date': datetime(2018, 4, 21, 19, 36, 47),
        'advisory_name': 'RHBA-2017:27760-01',
        'issue_date': datetime(2018, 3, 14, 5, 53, 25),
        'product_short_name': 'release-e2e-test',
        'content_types': ['docker'],
        'status_time': datetime(2018, 3, 14, 7, 53, 25),
        'state': 'DROPPED_NO_SHIP',
        'id_': '123456'
    })[0]
    fm_event = FreshmakerEvent.get_or_create({
        'event_type_id': 8,
        'id_': '1180',
        'message_id': 'ID:messaging-devops-broker01.test',
        'state': 2,
        'state_name': 'COMPLETE',
        'state_reason': 'All container images have been rebuilt.',
        'time_created': datetime(2018, 8, 13, 10, 36, 47),
        'time_done': datetime(2018, 8, 13, 12, 45, 47)
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
        'completion_time': datetime(2018, 8, 17, 13, 55, 47),
        'creation_time': datetime(2018, 8, 17, 8, 32, 47),
        'epoch': '0',
        'id_': '811',
        'name': 'some_build',
        'release': '4.el7_4_as',
        'start_time': datetime(2018, 8, 17, 8, 32, 47),
        'state': 2,
        'version': '1.7.5'
    })[0]

    # Longest story
    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory, {'time_attached': datetime(2018, 6, 13, 10, 36, 47)})
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.successful_koji_builds.connect(cb)
    fm_event.successful_koji_builds.connect(cb_two)

    # Unique partial stories
    commit_two.resolved_bugs.connect(bug_two)
    commit_two.koji_builds.connect(build)
    build.advisories.connect(advisory_two, {'time_attached': datetime(2018, 4, 21, 19, 36, 47)})

    rv = client.get('/api/v1/allstories/{0}/{1}'.format(resource, uid))
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_get_stories_fallback(client):
    """Test getting all the stories for a resource and falling back to a different label."""
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

    build.advisories.connect(advisory, {'time_attached': datetime(2017, 4, 3, 14, 47, 23)})
    expected = [{
        'data': [
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-02',
                    'content_types': ['docker'],
                    'created_at': '2017-04-03T14:47:23Z',
                    'display_name': 'RHBA-2017:2251-02',
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
                }],
                'commit': None,
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
                'display_name': u'slf4j-1.7.4-4.el7_4',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'tags': [],
                'timeline_timestamp': '2017-04-02T19:39:06Z',
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
                'update_date': '2017-08-01T07:16:00Z',
                'timeline_timestamp': '2017-04-03T14:47:23Z'
            }
        ],
        'meta': {
            'requested_node_index': 0,
            'story_related_nodes_forward': [0, 0],
            'story_related_nodes_backward': [0, 0],
            'wait_times': [68897.0],
            'total_lead_time': 10440285.0,
            'total_processing_time': 10371388.0,
            'processing_time_flag': False,
            'total_wait_time': 68897.0,
            'story_type': 'container'
        }
    }]

    rv = client.get('/api/v1/allstories/containerkojibuild/2345?fallback=kojibuild')
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected
