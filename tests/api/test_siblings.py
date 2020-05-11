# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

import pytest

from estuary.models.koji import KojiBuild, ContainerKojiBuild, ModuleKojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory, ContainerAdvisory
from estuary.models.freshmaker import FreshmakerEvent


@pytest.mark.parametrize('resource,uid,backward_rel,expected', [
    ('advisory', '27825', True, {
        'data': [
            {
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51Z',
                        'advisory_name': 'RHBA-2017:2251-02',
                        'created_at': '2017-04-03T14:47:23Z',
                        'display_name': 'RHBA-2017:2251-02',
                        'id': '27825',
                        'issue_date': '2017-08-01T05:59:34Z',
                        'product_name': 'Red Hat Enterprise Linux',
                        'release_date': None,
                        'resource_type': 'Advisory',
                        'security_impact': 'None',
                        'security_sla': None,
                        'state': 'SHIPPED_LIVE',
                        'status_time': '2017-08-01T15:43:51Z',
                        'synopsis': 'cifs-utils bug fix update',
                        'update_date': '2017-08-01T07:16:00Z'
                    }
                ],
                'commit': None,
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf3j-1.7.1-4.el6_3',
                'epoch': '0',
                'id': '3456',
                'module_builds': [

                ],
                'name': 'slf3j',
                'owner': None,
                'release': '4.el6_3',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 2,
                'version': '1.7.1'
            },
            {
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51Z',
                        'advisory_name': 'RHBA-2017:2251-02',
                        'created_at': '2017-04-03T14:47:23Z',
                        'display_name': 'RHBA-2017:2251-02',
                        'id': '27825',
                        'issue_date': '2017-08-01T05:59:34Z',
                        'product_name': 'Red Hat Enterprise Linux',
                        'release_date': None,
                        'resource_type': 'Advisory',
                        'security_impact': 'None',
                        'security_sla': None,
                        'state': 'SHIPPED_LIVE',
                        'status_time': '2017-08-01T15:43:51Z',
                        'synopsis': 'cifs-utils bug fix update',
                        'update_date': '2017-08-01T07:16:00Z'
                    }
                ],
                'commit': {
                    'author_date': '2017-04-26T11:44:38Z',
                    'commit_date': '2017-04-26T11:44:38Z',
                    'hash': '8a63adb248ba633e200067e1ad6dc61931727bad',
                    'log_message': 'Related: #12345 - fix xyz',
                    'display_name': 'commit #8a63adb',
                    'resource_type': 'DistGitCommit',
                },
                'completion_time': '2017-04-02T19:39:06Z',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': 'slf4j-1.7.4-4.el7_4',
                'epoch': '0',
                'id': '2345',
                'module_builds': [

                ],
                'name': 'slf4j',
                'owner': None,
                'release': '4.el7_4',
                'resource_type': 'KojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'version': '1.7.4'
            }
        ],
        'meta': {
            'description': 'Builds attached to RHBA-2017:2251-02'
        }
    }),
    ('freshmakerevent', '1180', True, {
        'data': [
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-02',
                'assigned_to': None,
                'attached_bugs': [],
                'attached_builds': [
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'display_name': 'slf3j-1.7.1-4.el6_3',
                        'epoch': '0',
                        'id': '3456',
                        'name': 'slf3j',
                        'release': '4.el6_3',
                        'resource_type': 'KojiBuild',
                        'start_time': '2017-04-02T19:39:06Z',
                        'state': 2,
                        'version': '1.7.1'},
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'resource_type': 'KojiBuild',
                        'display_name': 'slf4j-1.7.4-4.el7_4',
                        'epoch': '0',
                        'id': '2345',
                        'name': 'slf4j',
                        'release': '4.el7_4',
                        'start_time': '2017-04-02T19:39:06Z',
                        'resource_type': 'KojiBuild',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '27825',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'release_date': None,
                'reporter': None,
                'resource_type': 'Advisory',
                'display_name': 'RHBA-2017:2251-02',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'triggered_freshmaker_event': [{
                    'display_name': 'Freshmaker event 1180',
                    'id': '1180',
                    'resource_type': 'FreshmakerEvent',
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                }],
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'description': 'Advisories that triggered Freshmaker event 1180'
        }
    }),
    ('containeradvisory', '12327', True, {
        'data': [
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-03',
                    'created_at': '2017-04-03T14:47:23Z',
                    'display_name': 'RHBA-2017:2251-03',
                    'id': '12327',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name': 'Red Hat Enterprise Linux',
                    'release_date': None,
                    'resource_type': 'ContainerAdvisory',
                    'security_impact': 'None',
                    'security_sla': None,
                    'state': 'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51Z',
                    'synopsis': 'cifs-utils bug fix update',
                    'update_date': '2017-08-01T07:16:00Z'
                }],
                'commit': None,
                'completion_time': '2018-04-02T19:39:06Z',
                'creation_time': '2018-04-02T19:39:06Z',
                'epoch': '0',
                'display_name': 'some_build-1.7.5-4.el7_4_as',
                'id': '811',
                'module_builds': [],
                'name': 'some_build',
                'operator': False,
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'start_time': '2018-04-02T19:39:06Z',
                'state': 2,
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'id': '1180',
                    'resource_type': 'FreshmakerEvent',
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.5'
            },
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-03',
                    'created_at': '2017-04-03T14:47:23Z',
                    'display_name': 'RHBA-2017:2251-03',
                    'id': '12327',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name': 'Red Hat Enterprise Linux',
                    'release_date': None,
                    'resource_type': 'ContainerAdvisory',
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
                'id': '710',
                'module_builds': [],
                'name': 'slf4j_2',
                'operator': False,
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'id': '1180',
                    'resource_type': 'FreshmakerEvent',
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.4'
            }
        ],
        'meta': {
            'description': 'Container builds attached to RHBA-2017:2251-03'
        }
    }),
    ('containerkojibuild', '710', False, {
        'data': [
            {
                'actual_ship_date': '2017-08-01T15:43:51Z',
                'advisory_name': 'RHBA-2017:2251-03',
                'assigned_to': None,
                'attached_bugs': [],
                'attached_builds': [
                    {
                        'completion_time': '2018-04-02T19:39:06Z',
                        'creation_time': '2018-04-02T19:39:06Z',
                        'display_name': 'some_build-1.7.5-4.el7_4_as',
                        'epoch': '0',
                        'id': '811',
                        'name': 'some_build',
                        'operator': False,
                        'original_nvr': None,
                        'release': '4.el7_4_as',
                        'resource_type': 'ContainerKojiBuild',
                        'start_time': '2018-04-02T19:39:06Z',
                        'state': 2,
                        'version': '1.7.5'},
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'resource_type': 'ContainerKojiBuild',
                        'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                        'epoch': '0',
                        'id': '710',
                        'name': 'slf4j_2',
                        'operator': False,
                        'original_nvr': None,
                        'release': '4.el7_4_as',
                        'start_time': '2017-04-02T19:39:06Z',
                        'resource_type': 'ContainerKojiBuild',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ],
                'created_at': '2017-04-03T14:47:23Z',
                'id': '12327',
                'issue_date': '2017-08-01T05:59:34Z',
                'product_name': 'Red Hat Enterprise Linux',
                'release_date': None,
                'reporter': None,
                'resource_type': 'ContainerAdvisory',
                'display_name': 'RHBA-2017:2251-03',
                'security_impact': 'None',
                'security_sla': None,
                'state': 'SHIPPED_LIVE',
                'status_time': '2017-08-01T15:43:51Z',
                'synopsis': 'cifs-utils bug fix update',
                'triggered_freshmaker_event': [],
                'update_date': '2017-08-01T07:16:00Z'
            }
        ],
        'meta': {
            'description': 'Container advisories that contain slf4j_2-1.7.4-4.el7_4_as'
        }
    })
])
def test_node_siblings(client, resource, uid, backward_rel, expected):
    """Tests getting the siblings of an artifact's adjacent node in the story path."""
    bug = BugzillaBug.get_or_create({
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
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '27825',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]
    fm_event = FreshmakerEvent.get_or_create({
        'id_': '1180',
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
    ca = ContainerAdvisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-03',
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '12327',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]

    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory)
    build_two.advisories.connect(advisory)
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.successful_koji_builds.connect(cb)
    fm_event.successful_koji_builds.connect(cb_two)
    ca.attached_builds.connect(cb)
    ca.attached_builds.connect(cb_two)

    url = '/api/v1/siblings/{0}/{1}'.format(resource, uid)
    if backward_rel:
        url = '{0}?backward_rel=true'.format(url)
    rv = client.get(url)
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


@pytest.mark.parametrize('resource,uid,backward_rel,expected', [
    ('advisory', '27825', True, {
        'data': [
            {
                'advisories': [
                    {
                        'actual_ship_date': '2017-08-01T15:43:51Z',
                        'advisory_name': 'RHBA-2017:2251-02',
                        'created_at': '2017-04-03T14:47:23Z',
                        'display_name': 'RHBA-2017:2251-02',
                        'id': '27825',
                        'issue_date': '2017-08-01T05:59:34Z',
                        'product_name': 'Red Hat Enterprise Linux',
                        'release_date': None,
                        'resource_type': 'Advisory',
                        'security_impact': 'None',
                        'security_sla': None,
                        'state': 'SHIPPED_LIVE',
                        'status_time': '2017-08-01T15:43:51Z',
                        'synopsis': 'cifs-utils bug fix update',
                        'update_date': '2017-08-01T07:16:00Z'
                    }
                ],
                'commit': None,
                'completion_time': '2017-04-02T19:39:06Z',
                'components': [
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'display_name': 'slf3j-1.7.1-4.el6_3',
                        'epoch': '0',
                        'id': '3456',
                        'name': 'slf3j',
                        'release': '4.el6_3',
                        'start_time': '2017-04-02T19:39:06Z',
                        'resource_type': 'KojiBuild',
                        'state': 2,
                        'version': '1.7.1'
                    },
                    {
                        'completion_time': '2017-04-02T19:39:06Z',
                        'creation_time': '2017-04-02T19:39:06Z',
                        'display_name': 'slf4j-1.7.4-4.el7_4',
                        'epoch': '0',
                        'id': '2345',
                        'name': 'slf4j',
                        'release': '4.el7_4',
                        'start_time': '2017-04-02T19:39:06Z',
                        'resource_type': 'KojiBuild',
                        'state': 1,
                        'version': '1.7.4'
                    }
                ],
                'context': 'a2037af3',
                'creation_time': '2017-04-02T19:39:06Z',
                'display_name': '389-ds-None-20180805121332.a2037af3',
                'epoch': '0',
                'id': '2345',
                'mbs_id': 1338,
                'module_builds': [

                ],
                'module_name': '389-ds',
                'module_stream': '1.4',
                'module_version': '20180805121332',
                'name': '389-ds',
                'owner': None,
                'release': '20180805121332.a2037af3',
                'resource_type': 'ModuleKojiBuild',
                'start_time': '2017-04-02T19:39:06Z',
                'state': None,
                'version': None
            }
        ],
        'meta':{
            'description': 'Module builds attached to RHBA-2017:2251-02'
        }
    }),
    ('containeradvisory', '12327', True, {
        'data': [
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-03',
                    'created_at': '2017-04-03T14:47:23Z',
                    'display_name': 'RHBA-2017:2251-03',
                    'id': '12327',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name': 'Red Hat Enterprise Linux',
                    'release_date': None,
                    'resource_type': 'ContainerAdvisory',
                    'security_impact': 'None',
                    'security_sla': None,
                    'state': 'SHIPPED_LIVE',
                    'status_time': '2017-08-01T15:43:51Z',
                    'synopsis': 'cifs-utils bug fix update',
                    'update_date': '2017-08-01T07:16:00Z'
                }],
                'commit': None,
                'completion_time': '2018-04-02T19:39:06Z',
                'creation_time': '2018-04-02T19:39:06Z',
                'epoch': '0',
                'display_name': 'some_build-1.7.5-4.el7_4_as',
                'id': '811',
                'module_builds': [],
                'name': 'some_build',
                'operator': False,
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'start_time': '2018-04-02T19:39:06Z',
                'state': 2,
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'id': '1180',
                    'resource_type': 'FreshmakerEvent',
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.5'
            },
            {
                'advisories': [{
                    'actual_ship_date': '2017-08-01T15:43:51Z',
                    'advisory_name': 'RHBA-2017:2251-03',
                    'created_at': '2017-04-03T14:47:23Z',
                    'display_name': 'RHBA-2017:2251-03',
                    'id': '12327',
                    'issue_date': '2017-08-01T05:59:34Z',
                    'product_name': 'Red Hat Enterprise Linux',
                    'release_date': None,
                    'resource_type': 'ContainerAdvisory',
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
                'id': '710',
                'module_builds': [],
                'name': 'slf4j_2',
                'operator': False,
                'original_nvr': None,
                'owner': None,
                'release': '4.el7_4_as',
                'resource_type': 'ContainerKojiBuild',
                'display_name': 'slf4j_2-1.7.4-4.el7_4_as',
                'start_time': '2017-04-02T19:39:06Z',
                'state': 1,
                'triggered_by_freshmaker_event': {
                    'display_name': 'Freshmaker event 1180',
                    'id': '1180',
                    'resource_type': 'FreshmakerEvent',
                    'state_name': 'COMPLETE',
                    'state_reason': 'All container images have been rebuilt.',
                    'time_created': '2019-08-21T13:42:20Z',
                    'time_done': '2099-08-21T13:42:20Z'
                },
                'version': '1.7.4'
            }
        ],
        'meta': {
            'description': 'Container builds attached to RHBA-2017:2251-03'
        }
    })
])
def test_module_story_node_siblings(client, resource, uid, backward_rel, expected):
    """Tests getting the siblings of an artifact's adjacent node in the module story path."""
    bug = BugzillaBug.get_or_create({
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
    advisory = Advisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-02',
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '27825',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]
    fm_event = FreshmakerEvent.get_or_create({
        'id_': '1180',
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
    ca = ContainerAdvisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-03',
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '12327',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]

    commit.resolved_bugs.connect(bug)
    commit.koji_builds.connect(build)
    build.advisories.connect(advisory)
    build_two.advisories.connect(advisory)
    fm_event.triggered_by_advisory.connect(advisory)
    fm_event.successful_koji_builds.connect(cb)
    fm_event.successful_koji_builds.connect(cb_two)
    ca.attached_builds.connect(cb)
    ca.attached_builds.connect(cb_two)
    module_build.components.connect(build)
    module_build.components.connect(build_two)
    module_build.advisories.connect(advisory)

    url = '/api/v1/siblings/{0}/{1}?story_type=module'.format(resource, uid)
    if backward_rel:
        url = '{0}&backward_rel=true'.format(url)
    rv = client.get(url)
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_first_node_of_story(client):
    """Tests getting the siblings for the first node of the story with backward_rel=true."""
    BugzillaBug.get_or_create({
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
    })[0]

    expected = {
        'message': 'Siblings cannot be determined on this kind of resource',
        'status': 400
    }

    rv = client.get('/api/v1/siblings/bugzillabug/5555?backward_rel=true')
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_reverse_flag(client):
    """Tests getting the siblings for when backward_rel=false and passing in a ContainerAdvisory."""
    ContainerAdvisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-03',
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '12327',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]

    expected = {
        'message': 'Siblings cannot be determined on this kind of resource',
        'status': 400
    }

    rv = client.get('/api/v1/siblings/containeradvisory/12327')
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected


def test_story_path_flag_invalid(client):
    """Tests getting the siblings for when the story_path flag is invalid."""
    Advisory.get_or_create({
        'actual_ship_date': datetime(2017, 8, 1, 15, 43, 51),
        'advisory_name': 'RHBA-2017:2251-03',
        'created_at': datetime(2017, 4, 3, 14, 47, 23),
        'id_': '12327',
        'issue_date': datetime(2017, 8, 1, 5, 59, 34),
        'product_name': 'Red Hat Enterprise Linux',
        'security_impact': 'None',
        'state': 'SHIPPED_LIVE',
        'status_time': datetime(2017, 8, 1, 15, 43, 51),
        'synopsis': 'cifs-utils bug fix update',
        'update_date': datetime(2017, 8, 1, 7, 16)
    })[0]

    expected = {
        'message': ('Supplied story type is invalid. Select from: ModuleStoryManager, '
                    'ContainerStoryManager'),
        'status': 400}

    rv = client.get('/api/v1/siblings/advisory/12327?story_type=random')
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8')) == expected
