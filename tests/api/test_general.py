# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import json
from datetime import datetime

import pytest

from purview import version
from purview.models.user import User
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitPush, DistGitCommit
from purview.models.errata import Advisory, AdvisoryState
from purview.models.freshmaker import FreshmakerEvent, ContainerBuilds
from purview.models.koji import KojiBuild, KojiTask, KojiTag


def test_about(client):
    """Test the /api/v1/about route."""
    rv = client.get('/api/v1/about')
    assert json.loads(rv.data.decode('utf-8')) == {'version': version}


@pytest.mark.parametrize('model,resource,uid,test_input', [
    (BugzillaBug, 'bugzillabug', '12345', {
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
        'id_': '12345',
        'status': 'CLOSED'
    }),
    (DistGitPush, 'distgitpush', '12345', {
        'push_ip': '10.0.0.1',
        'push_date': datetime(2018, 3, 14, 5, 53, 19),
        'id_': '12345'
    }),
    (DistGitCommit, 'distgitcommit', 'f4dfc64c10a90492303e4f14ad3549a1a2b13575', {
        'commit_date': datetime(2018, 3, 14, 5, 52, 19),
        'author_date': datetime(2018, 3, 14, 5, 53, 25),
        'log_message': 'Repo creation',
        'hash_': 'f4dfc64c10a90492303e4f14ad3549a1a2b13575'
    }),
    (Advisory, 'advisory', '12345', {
        'security_impact': 'None',
        'created_at': datetime(2018, 3, 14, 5, 53, 25),
        'synopsis': 'This is a synopsis of a test advisory.',
        'type': 'RHBA',
        'product_name': 'Release End2End Test',
        'update_date': datetime(2018, 3, 14, 7, 53, 25),
        'advisory_name': 'RHBA-2017:27760-01',
        'issue_date': datetime(2018, 3, 14, 5, 53, 25),
        'updated_at': datetime(2018, 3, 14, 7, 53, 25),
        'product_short_name': 'release-e2e-test',
        'content_types': ['docker'],
        'status_time': datetime(2018, 3, 14, 7, 53, 25),
        'state': 'DROPPED_NO_SHIP',
        'id_': '12345'
    }),
    (AdvisoryState, 'advisorystate', '12345', {
        'id_': '12345',
        'name': 'NEW_FILES',
        'created_at': datetime(2018, 3, 14, 5, 53, 25),
        'updated_at': datetime(2018, 3, 14, 5, 53, 25),
    }),
    (FreshmakerEvent, 'freshmakerevent', '12345', {
        'id_': '12345',
        'state_reason': 'No container images to rebuild for advisory \'RHSA-2018:1234\'',
        'state_name': 'SKIPPED',
        'message_id': 'Some ID',
        'state': 4,
        'url': '/api/1/events/12345',
        'event_type_id': 8
    }),
    (ContainerBuilds, 'containerbuilds', '12345', {
        'rebuilt_nvr': 'python-3.6-123.1522949725',
        'type_name': 'IMAGE',
        'state_reason': 'Some reason',
        'time_completed': datetime(2018, 3, 14, 5, 53, 25),
        'original_nvr': 'e2e-container-test-product-docker-7.3-1458',
        'type_': 1,
        'time_submitted': datetime(2018, 3, 14, 5, 48, 5),
        'url': '/api/1/builds/12345',
        'event_id': 345,
        'state_name': 'FAILED',
        'build_id': 56789,
        'name': 'e2e-container-test-product-docker',
        'state': 2,
        'id_': '12345'
    }),
    (KojiBuild, 'kojibuild', '12345', {
        'creation_time': datetime(2018, 3, 14, 5, 51, 8),
        'start_time': datetime(2018, 3, 14, 5, 51, 8),
        'completion_time': datetime(2018, 3, 14, 5, 53, 25),
        'release': '1.el7',
        'name': 'python-requests',
        'state': 1,
        'id_': '12345',
        'version': '1.13'
    }),
    (KojiTask, 'kojitask', '12345', {
        'start_time': datetime(2018, 3, 14, 5, 51, 15),
        'completion_time': datetime(2018, 3, 14, 5, 55, 8),
        'method': 'buildSRPMFromSCM',
        'create_time': datetime(2018, 3, 14, 5, 51, 8),
        'weight': 1,
        'arch': 'noarch',
        'id_': '12345',
        'state': 2,
        'priority': 19
    }),
    (KojiTag, 'kojitag', '12345', {
        'name': 'some-tag',
        'id_': '12345'
    }),
    (User, 'user', 'tbrady', {
        'username': 'tbrady',
        'email': 'tom.brady@domain.local'
    })
])
def test_get_resource_relationship_false(client, model, resource, uid, test_input):
    """Test getting a resource from Neo4j without its relationships."""
    item = model.get_or_create(test_input)[0]
    rv = client.get('/api/v1/{0}/{1}?relationship=false'.format(resource, uid))
    assert rv.status_code == 200
    assert json.loads(rv.data.decode('utf-8')) == item.serialized


@pytest.mark.parametrize('resource', ['distgitrepo', 'distgitbranch'])
def test_get_on_model_wo_uid(client, resource):
    """Test that an error is returned when a resource with a UniqueIdProperty is requested."""
    rv = client.get('/api/v1/{0}/some_repo'.format(resource))
    assert rv.status_code == 400
    invalid_msg = ('The requested resource "{0}" is invalid. Choose from the following: '
                   'advisory, advisorystate, bugzillabug, containerbuilds, distgitcommit, '
                   'distgitpush, freshmakerevent, kojibuild, kojitag, kojitask, and user.'
                   .format(resource))
    assert json.loads(rv.data.decode('utf-8')) == {'message': invalid_msg, 'status': 400}


def test_get_resources(client):
    """Test the /api/v1/story route."""
    rv = client.get('/api/v1/story')
    assert rv.status_code == 200
    expected = {
        'advisory': 'id',
        'bugzillabug': 'id',
        'containerbuilds': 'id',
        'distgitcommit': 'hash',
        'freshmakerevent': 'id',
        'kojibuild': 'id',
    }
    assert json.loads(rv.data.decode('utf-8')) == expected
