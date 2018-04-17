# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import json
from datetime import datetime

from purview.models.user import User
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitCommit
from purview.models.errata import Advisory


def test_get_bug(client):
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
    bug.assignee.connect(mprahl)
    bug.qa_contact.connect(jsmith)
    bug.reporter.connect(tbrady)
    commit.resolved_bugs.connect(bug)
    commit_two.resolved_bugs.connect(bug)
    commit_three.reverted_bugs.connect(bug)
    advisory.attached_bugs.connect(bug)

    rv = client.get('/api/v1/bugzillabug/12345')
    assert rv.status_code == 200
    expected = {
        'assignee': [{
            'email': 'matt.prahl@domain.local',
            'name': None,
            'username': 'mprahl'
        }],
        'attached_advisories': [{
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
        'classification': 'Red Hat',
        'creation_time': '2017-04-02T19:39:06+00:00',
        'id': '12345',
        'modified_time': '2018-02-07T19:30:47+00:00',
        'priority': 'high',
        'product_name': 'Red Hat Enterprise Linux',
        'product_version': '7.5',
        'qa_contact': [{
            'email': 'jsmith@domain.local',
            'name': None,
            'username': 'jsmith'
        }],
        'related_by_commits': [],
        'reporter': [{
            'email': 'tom.brady@domain.local',
            'name': None,
            'username': 'tbrady'}],
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
            }],
        'reverted_by_commits': [{
            'author_date': '2017-04-27T11:44:38+00:00',
            'commit_date': '2017-04-27T11:44:38+00:00',
            'hash': '5663adb248ba633e205067e1ad6dc61931727123',
            'log_message': 'Revert: #12345'
        }],
        'severity': 'low',
        'short_description': 'Some description',
        'status': 'VERIFIED',
        'target_milestone': 'rc',
        'votes': 0
    }
    assert json.loads(rv.data.decode('utf-8')) == expected
