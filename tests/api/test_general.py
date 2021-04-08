# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import json
from datetime import datetime

import pytest

from estuary import version
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory
from estuary.models.freshmaker import FreshmakerEvent
from estuary.models.koji import ContainerKojiBuild, KojiBuild
from estuary.models.user import User


def test_about(client):
    """Test the /api/v1/about route."""
    rv = client.get('/api/v1/about')
    assert json.loads(rv.data.decode('utf-8')) == {
        'auth_required': False,
        'version': version
    }


@pytest.mark.parametrize('model,resource,uid,test_input', [
    (BugzillaBug, 'bugzillabug', '12345', {
        'creation_time': datetime(2017, 4, 1, 17, 41, 4),
        'severity': 'medium',
        'short_description': 'some description',
        'product_version': '7.2',
        'priority': 'unspecified',
        'product_name': 'Red Hat Enterprise Linux 7',
        'resolution': 'DUPLICATE',
        'target_milestone': 'rc',
        'modified_time': datetime(2018, 3, 14, 5, 53, 19),
        'id_': '12345',
        'status': 'CLOSED'
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
        'product_name': 'Release End2End Test',
        'update_date': datetime(2018, 3, 14, 7, 53, 25),
        'advisory_name': 'RHBA-2017:27760-01',
        'issue_date': datetime(2018, 3, 14, 5, 53, 25),
        'status_time': datetime(2018, 3, 14, 7, 53, 25),
        'state': 'DROPPED_NO_SHIP',
        'id_': '12345'
    }),
    (FreshmakerEvent, 'freshmakerevent', '12345', {
        'id_': '12345',
        'state_reason': 'No container images to rebuild for advisory \'RHSA-2018:1234\'',
        'state_name': 'SKIPPED',
    }),
    (ContainerKojiBuild, 'containerkojibuild', '710', {
        'completion_time': datetime(2017, 4, 2, 19, 39, 6),
        'creation_time': datetime(2017, 4, 2, 19, 39, 6),
        'epoch': '0',
        'id_': '710',
        'module_builds': [],
        'name': 'slf4j_2',
        'release': '4.el7_4_as',
        'start_time': datetime(2017, 4, 2, 19, 39, 6),
        'state': 1,
        'version': '1.7.4'
    }),
    (KojiBuild, 'kojibuild', '12345', {
        'creation_time': datetime(2018, 3, 14, 5, 51, 8),
        'start_time': datetime(2018, 3, 14, 5, 51, 8),
        'completion_time': datetime(2018, 3, 14, 5, 53, 25),
        'release': '1.el7',
        'name': 'python-requests',
        'module_builds': [],
        'state': 1,
        'id_': '12345',
        'version': '1.13'
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


@pytest.mark.parametrize('resource', ['distgitrepo'])
def test_get_on_model_wo_uid(client, resource):
    """Test that an error is returned when a resource with a UniqueIdProperty is requested."""
    rv = client.get('/api/v1/{0}/some_repo'.format(resource))
    assert rv.status_code == 400
    invalid_msg = ('The requested resource "{0}" is invalid. Choose from the following: '
                   'advisory, bugzillabug, containeradvisory, containerkojibuild, distgitcommit, '
                   'freshmakerevent, freshmakerbuild, kojibuild, modulekojibuild, and '
                   'user.'.format(resource))
    assert json.loads(rv.data.decode('utf-8')) == {'message': invalid_msg, 'status': 400}
