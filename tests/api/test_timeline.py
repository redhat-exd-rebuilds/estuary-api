# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime
import logging

from mock import patch, Mock
import pytz
import pytest

import estuary.utils.story
from tests import helpers


def test_full_timeline():
    """Test the data relating to the timeline with a full story."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0)
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 20),
        'completion_time': datetime(2019, 1, 1, 0, 0, 30)
    })
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '4444',
        'state': 'SHIPPED_LIVE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50)
    })
    event = helpers.make_artifact('FreshmakerEvent', **{
        'id_': '5555',
        'time_created': datetime(2019, 1, 1, 0, 1, 0),
        'time_done': datetime(2019, 1, 1, 0, 1, 30),
        'state_name': 'COMPLETE'
    })
    c_build = helpers.make_artifact('ContainerKojiBuild', **{
        'id_': '6666',
        'creation_time': datetime(2019, 1, 1, 0, 1, 20),
        'completion_time': datetime(2019, 1, 1, 0, 1, 30)
    })
    c_advisory = helpers.make_artifact('ContainerAdvisory', **{
        'id_': '7777',
        'state': 'SHIPPED_LIVE',
        'created_at': datetime(2019, 1, 1, 0, 1, 40),
        'status_time': datetime(2019, 1, 1, 0, 1, 50)
    })

    advisory.attached_builds.connect(build, {'time_attached': datetime(2019, 1, 1, 0, 0, 40)})
    c_advisory.attached_builds.connect(c_build, {'time_attached': datetime(2019, 1, 1, 0, 1, 40)})

    results = [bug, commit, build, advisory, event, c_build, c_advisory]
    base_instance = estuary.utils.story.BaseStoryManager()
    processing_time, flag = base_instance.get_total_processing_time(results)
    lead_time = base_instance.get_total_lead_time(results)
    wait_times, total_wait_time = base_instance.get_wait_times(results)

    assert processing_time == 60.0
    assert flag is False
    assert lead_time == 110.0
    assert wait_times == [10.0, 10.0, 10.0, 10.0, 20.0, 10.0]
    assert total_wait_time == 50.0


def test_full_module_timeline():
    """Test the data relating to the timeline with a full module story."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0)
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 20),
        'completion_time': datetime(2019, 1, 1, 0, 0, 30)
    })
    m_build = helpers.make_artifact('ModuleKojiBuild', **{
        'id_': '4444',
        'creation_time': datetime(2019, 1, 1, 0, 0, 40),
        'completion_time': datetime(2019, 1, 1, 0, 0, 50)
    })
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '5555',
        'state': 'DROPPED_NO_SHIP',
        'created_at': datetime(2019, 1, 1, 0, 1, 0),
        'status_time': datetime(2019, 1, 1, 0, 1, 10)
    })

    advisory.attached_builds.connect(m_build, {'time_attached': datetime(2019, 1, 1, 0, 1, 0)})

    results = [bug, commit, build, m_build, advisory]
    base_instance = estuary.utils.story.BaseStoryManager()
    processing_time, flag = base_instance.get_total_processing_time(results)
    lead_time = base_instance.get_total_lead_time(results)
    wait_times, total_wait_time = base_instance.get_wait_times(results)

    assert processing_time == 30.0
    assert flag is False
    assert lead_time == 70.0
    assert wait_times == [10.0, 10.0, 10.0, 10.0]
    assert total_wait_time == 40.0


@pytest.mark.parametrize('label,data,expected', [
    ('BugzillaBug', {
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0)
    }, [0, 0, [0], 0, False]),
    ('DistGitCommit', {
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    }, [0, 0, [0], 0, False]),
    ('KojiBuild', {
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 20),
        'completion_time': datetime(2019, 1, 1, 0, 0, 30)
    }, [10.0, 10.0, [0], 0, False]),
    ('Advisory', {
        'id_': '4444',
        'state': 'SHIPPED_LIVE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50)
    }, [0, 10.0, [0], 0, True]),
    ('FreshmakerEvent', {
        'id_': '5555',
        'time_created': datetime(2019, 1, 1, 0, 1, 0),
        'time_done': datetime(2019, 1, 1, 0, 1, 10),
        'state_name': 'COMPLETE'
    }, [10.0, 10.0, [0], 0, False]),
    ('ContainerKojiBuild', {
        'id_': '6666',
        'creation_time': datetime(2019, 1, 1, 0, 1, 20),
        'completion_time': datetime(2019, 1, 1, 0, 1, 30)
    }, [10.0, 10.0, [0], 0, False]),
    ('ContainerAdvisory', {
        'id_': '7777',
        'state': 'SHIPPED_LIVE',
        'created_at': datetime(2019, 1, 1, 0, 1, 40),
        'status_time': datetime(2019, 1, 1, 0, 1, 50)
    }, [0, 10.0, [0], 0, True]),
])
def test_individual_nodes(label, data, expected):
    """Test the data relating to the timeline with only one node."""
    artifact = helpers.make_artifact(label, **data)
    base_instance = estuary.utils.story.BaseStoryManager()
    processing_time, flag = base_instance.get_total_processing_time([artifact])
    lead_time = base_instance.get_total_lead_time([artifact])
    wait_times, total_wait_time = base_instance.get_wait_times([artifact])

    assert processing_time == expected[0]
    assert lead_time == expected[1]
    assert wait_times == expected[2]
    assert total_wait_time == expected[3]
    assert flag is expected[4]


def test_event_building():
    """Test the data relating to the timeline with an event still building."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0)
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 20),
        'completion_time': datetime(2019, 1, 1, 0, 0, 30)
    })
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '4444',
        'state': 'SHIPPED_LIVE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50)
    })
    event = helpers.make_artifact('FreshmakerEvent', **{
        'id_': '5555',
        'time_created': datetime(2019, 1, 1, 0, 1, 0),
        'time_done': None,
        'state_name': 'BUILDING'
    })

    advisory.attached_builds.connect(build, {'time_attached': datetime(2019, 1, 1, 0, 0, 40)})

    results = [bug, commit, build, advisory, event]

    with patch.object(estuary.utils.story, 'datetime', Mock(wraps=datetime)) as datetime_patch:
        datetime_patch.utcnow.return_value = datetime(2019, 1, 1, 0, 1, 20, tzinfo=pytz.utc)
        base_instance = estuary.utils.story.BaseStoryManager()
        processing_time, flag = base_instance.get_total_processing_time(results)
        lead_time = base_instance.get_total_lead_time(results)
        wait_times, total_wait_time = base_instance.get_wait_times(results)

    assert processing_time == 40.0
    assert flag is False
    assert lead_time == 80.0
    assert wait_times == [10.0, 10.0, 10.0, 10.0]
    assert total_wait_time == 40.0


def test_build_building():
    """Test the data relating to the timeline with a build still building."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0)
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 20),
        'completion_time': datetime(2019, 1, 1, 0, 0, 30)
    })
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '4444',
        'state': 'SHIPPED_LIVE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50)
    })
    event = helpers.make_artifact('FreshmakerEvent', **{
        'id_': '5555',
        'time_created': datetime(2019, 1, 1, 0, 1, 0),
        'time_done': datetime(2019, 1, 1, 0, 1, 10),
        'state_name': 'COMPLETE'
    })
    c_build = helpers.make_artifact('ContainerKojiBuild', **{
        'id_': '6666',
        'creation_time': datetime(2019, 1, 1, 0, 1, 20),
        'completion_time': None
    })

    advisory.attached_builds.connect(build, {'time_attached': datetime(2019, 1, 1, 0, 0, 40)})

    results = [bug, commit, build, advisory, event, c_build]

    with patch.object(estuary.utils.story, 'datetime', Mock(wraps=datetime)) as datetime_patch:
        datetime_patch.utcnow.return_value = datetime(2019, 1, 1, 0, 1, 50, tzinfo=pytz.utc)
        base_instance = estuary.utils.story.BaseStoryManager()
        processing_time, flag = base_instance.get_total_processing_time(results)
        lead_time = base_instance.get_total_lead_time(results)
        wait_times, total_wait_time = base_instance.get_wait_times(results)

    assert processing_time == 70.0
    assert flag is False
    assert lead_time == 110.0
    assert wait_times == [10.0, 10.0, 10.0, 10.0, 20.0]
    assert total_wait_time == 40.0


def test_advisory_in_qe():
    """Test the data relating to the timeline with an advisory in QE state."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0)
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 20),
        'completion_time': datetime(2019, 1, 1, 0, 0, 30)
    })
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '4444',
        'state': 'QE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50)
    })

    advisory.attached_builds.connect(build, {'time_attached': datetime(2019, 1, 1, 0, 0, 40)})

    results = [bug, commit, build, advisory]

    with patch.object(estuary.utils.story, 'datetime', Mock(wraps=datetime)) as datetime_patch:
        datetime_patch.utcnow.return_value = datetime(2019, 1, 1, 0, 1, 20, tzinfo=pytz.utc)
        base_instance = estuary.utils.story.BaseStoryManager()
        processing_time, flag = base_instance.get_total_processing_time(results)
        lead_time = base_instance.get_total_lead_time(results)
        wait_times, total_wait_time = base_instance.get_wait_times(results)

    assert processing_time == 50.0
    assert flag is False
    assert lead_time == 80.0
    assert wait_times == [10.0, 10.0, 10.0]
    assert total_wait_time == 30.0


def test_stubbed_artifact(caplog):
    """Test the data relating to the timeline with an artifact stubbed out."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': None
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 10)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': None
    })

    results = [bug, commit, build]
    base_instance = estuary.utils.story.BaseStoryManager()
    base_instance.get_total_lead_time(results)
    total_processing_time, flag = base_instance.get_total_processing_time(results)

    assert caplog.record_tuples == [
        ('estuary', logging.WARNING, 'While calculating the total lead time, a BugzillaBug with ID '
         '1111 was encountered without a creation time.'),
        ('estuary', logging.WARNING, 'While calculating the total processing time, a KojiBuild with'
         ' ID 3333 was encountered without a creation time.')
    ]
    assert flag is True


def test_nonlinear_data(caplog):
    """Test when a timeline has negative total times."""
    bug = helpers.make_artifact('BugzillaBug', **{
        'id_': '1111',
        'creation_time': datetime(2019, 1, 1, 0, 1, 10)
    })
    commit = helpers.make_artifact('DistGitCommit', **{
        'hash_': '2222',
        'commit_date': datetime(2019, 1, 1, 0, 0, 0)
    })
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 40),
        'completion_time': datetime(2019, 1, 1, 0, 0, 0)
    })

    results = [bug, commit, build]
    base_instance = estuary.utils.story.BaseStoryManager()
    total_lead_time = base_instance.get_total_lead_time(results)
    total_processing_time, flag = base_instance.get_total_processing_time(results)

    assert caplog.record_tuples == [
        ('estuary', logging.WARNING, 'A negative total lead time was calculated, in a story '
         'starting with a BugzillaBug with ID 1111 and ending with a KojiBuild with ID 3333.'),
        ('estuary', logging.WARNING, 'A negative processing time was calculated, with a KojiBuild '
         'with ID 3333.')
    ]
    assert total_lead_time == 0
    assert total_processing_time == 0
    assert flag is False


def test_event_no_time(caplog):
    """Test when a Freshmaker event in a completed state with no completion time."""
    event = helpers.make_artifact('FreshmakerEvent', **{
        'id_': '1111',
        'time_created': datetime(2019, 1, 1, 0, 0, 0),
        'time_done': None,
        'state_name': 'COMPLETE',
    })

    results = [event]
    base_instance = estuary.utils.story.BaseStoryManager()
    total_processing_time, flag = base_instance.get_total_processing_time(results)

    assert caplog.record_tuples == [
        ('estuary', logging.WARNING, 'While calculating the total processing time, a Freshmaker'
         'Event with ID 1111 was encountered without a completion time or subsequent build.')
    ]
    assert total_processing_time == 0
    assert flag is True


def test_unattached_build(caplog):
    """Test when there is an advisory without an attached build."""
    build = helpers.make_artifact('KojiBuild', **{
        'id_': '3333',
        'creation_time': datetime(2019, 1, 1, 0, 0, 0),
        'completion_time': datetime(2019, 1, 1, 0, 0, 20)
    })
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '4444',
        'state': 'QE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50),
        'attached_builds': None
    })
    event = helpers.make_artifact('FreshmakerEvent', **{
        'id_': '5555',
        'time_created': datetime(2019, 1, 1, 0, 1, 0),
        'time_done': datetime(2019, 1, 1, 0, 1, 10),
        'state_name': 'COMPLETE'
    })

    results = [build, advisory, event]
    base_instance = estuary.utils.story.BaseStoryManager()
    wait_times, total_wait_time = base_instance.get_wait_times(results)

    assert caplog.record_tuples == [
        ('estuary', logging.WARNING, 'While calculating the wait time, a Advisory with ID 4444 was'
         ' encountered without an attached build time.')
    ]


def test_no_attached_build(caplog):
    """Test when there is an advisory without an attached build."""
    advisory = helpers.make_artifact('Advisory', **{
        'id_': '4444',
        'state': 'QE',
        'created_at': datetime(2019, 1, 1, 0, 0, 40),
        'status_time': datetime(2019, 1, 1, 0, 0, 50),
        'attached_builds': None
    })
    event = helpers.make_artifact('FreshmakerEvent', **{
        'id_': '5555',
        'time_created': datetime(2019, 1, 1, 0, 1, 0),
        'time_done': datetime(2019, 1, 1, 0, 1, 10),
        'state_name': 'COMPLETE'
    })

    results = [advisory, event]
    base_instance = estuary.utils.story.BaseStoryManager()
    base_instance.get_total_processing_time(results)

    assert caplog.record_tuples == [
        ('estuary', logging.WARNING, 'While calculating the processing time, a Advisory with'
         ' ID 4444 was encountered without a build or creation time.')
    ]
