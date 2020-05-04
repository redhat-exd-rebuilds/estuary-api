# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

from estuary.models import names_to_model


def make_artifact(label, **kwargs):
    """Create an artifact with default data, combined with input data, if any."""
    if label not in names_to_model:
        raise ValueError('Invalid label')

    args = {}
    if label == 'BugzillaBug':
        args = {
            'creation_time': datetime(2019, 1, 1, 0, 0, 0),
            'id_': '12345',
            'modified_time': datetime(2019, 1, 1, 0, 0, 0),
            'priority': 'high',
            'product_name': 'Red Hat Enterprise Linux',
            'product_version': '7.5',
            'resolution': '',
            'severity': 'low',
            'short_description': 'Some description',
            'status': 'VERIFIED',
            'target_milestone': 'rc',
        }
    elif label == 'DistGitCommit':
        args = {
            'creation_time': datetime(2019, 1, 1, 0, 0, 10),
            'id': '12345',
            'modified_time': datetime(2019, 1, 1, 0, 0, 10),
            'priority': 'high',
            'product_name': 'Red Hat Enterprise Linux',
            'product_version': '7.5',
            'resolution': '',
            'severity': 'low',
            'short_description': 'Some description',
            'status': 'VERIFIED',
            'target_milestone': 'rc',
        }
    elif label == 'KojiBuild':
        args = {
            'completion_time': datetime(2019, 1, 1, 0, 0, 30),
            'creation_time': datetime(2019, 1, 1, 0, 0, 20),
            'epoch': '0',
            'id': '2345',
            'name': 'slf4j',
            'release': '4.el7_4',
            'start_time': datetime(2019, 1, 1, 0, 0, 20),
            'state': 1,
            'version': '1.7.4'
        }
    elif label == 'Advisory':
        args = {
            'actual_ship_date': datetime(2019, 1, 1, 0, 0, 40),
            'advisory_name': 'RHBA-2017:2251-02',
            'created_at': datetime(2019, 1, 1, 0, 0, 40),
            'id': '27825',
            'issue_date': datetime(2019, 1, 1, 0, 0, 40),
            'product_name': 'Red Hat Enterprise Linux',
            'release_date': None,
            'security_impact': 'None',
            'security_sla': None,
            'state': 'SHIPPED_LIVE',
            'status_time': datetime(2019, 1, 1, 0, 0, 50),
            'synopsis': 'cifs-utils bug fix update',
            'update_date': datetime(2019, 1, 1, 0, 0, 50),
        }
    elif label == 'FreshmakerEvent':
        args = {
            'event_type_id': 8,
            'id': '1180',
            'message_id': 'ID:messaging-devops-broker01.test',
            'state': 2,
            'state_name': 'COMPLETE',
            'state_reason': 'All container images have been rebuilt.',
            'time_created': datetime(2019, 1, 1, 0, 1, 0),
            'time_done': datetime(2019, 1, 1, 0, 1, 30)
        }
    elif label == 'ContainerKojiBuild':
        args = {
            'completion_time': datetime(2019, 1, 1, 0, 1, 30),
            'creation_time': datetime(2019, 1, 1, 0, 1, 20),
            'epoch': '0',
            'id': '710',
            'name': 'slf4j_2',
            'original_nvr': None,
            'release': '4.el7_4_as',
            'start_time': datetime(2019, 1, 1, 0, 1, 20),
            'state': 1,
            'version': '1.7.4'
        }
    elif label == 'ContainerAdvisory':
        args = {
            'actual_ship_date': datetime(2019, 1, 1, 0, 1, 40),
            'advisory_name': 'RHBA-2017:2251-03',
            'created_at': datetime(2019, 1, 1, 0, 1, 40),
            'id': '12327',
            'issue_date': datetime(2019, 1, 1, 0, 1, 40),
            'product_name': 'Red Hat Enterprise Linux',
            'release_date': None,
            'security_impact': 'None',
            'security_sla': None,
            'state': 'SHIPPED_LIVE',
            'status_time': datetime(2019, 1, 1, 0, 1, 50),
            'synopsis': 'cifs-utils bug fix update',
            'update_date': datetime(2019, 1, 1, 0, 1, 50),
        }
    elif label == 'ModuleKojiBuild':
        args = {
            'completion_time': datetime(2019, 1, 1, 0, 0, 50),
            'context': 'a2037af3',
            'creation_time': datetime(2019, 1, 1, 0, 0, 40),
            'epoch': '0',
            'id': '2345',
            'mbs_id': 1338,
            'module_name': '389-ds',
            'module_stream': '1.4',
            'module_version': '20180805121332',
            'name': '389-ds',
            'release': '20180805121332.a2037af3',
            'start_time': datetime(2019, 1, 1, 0, 0, 40),
            'state': None,
            'version': None
        }
    else:
        raise ValueError('Invalid label')

    args.update(**kwargs)

    artifact_class = names_to_model[label]
    return artifact_class.get_or_create(args)[0]
