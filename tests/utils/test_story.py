# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import pytest

from estuary.utils.story import BaseStoryManager, ContainerStoryManager


@pytest.mark.parametrize('display_name,label,backward,expected', [
    ('RHBZ#12345', 'BugzillaBug', False, 'Commits that resolved RHBZ#12345'),
    ('commit #1234567', 'DistGitCommit', False, 'Builds built by commit #1234567'),
    ('commit #1234567', 'DistGitCommit', True, 'Bugzilla bugs resolved by commit #1234567'),
    ('python-requests-1.10-3', 'KojiBuild', False, 'Advisories that contain '
        'python-requests-1.10-3'),
    ('python-requests-1.10-3', 'KojiBuild', True, 'Commits that built python-requests-1.10-3'),
    ('RHSA-2018:1700-02', 'Advisory', False, 'Freshmaker events triggered by RHSA-2018:1700-02'),
    ('RHSA-2018:1700-02', 'Advisory', True, 'Builds attached to RHSA-2018:1700-02'),
    ('Freshmaker event 123456', 'FreshmakerEvent', False, 'Container builds triggered by Freshmaker'
        ' event 123456'),
    ('Freshmaker event 123456', 'FreshmakerEvent', True, 'Advisories that triggered Freshmaker '
        'event 123456'),
    ('python-requests-1.10-3', 'ContainerKojiBuild', False, 'Container advisories that contain'
        ' python-requests-1.10-3'),
    ('python-requests-1.10-3', 'ContainerKojiBuild', True, 'Freshmaker events that triggered'
        ' python-requests-1.10-3'),
    ('RHBA-2018:1700-02', 'ContainerAdvisory', True, 'Container builds attached to '
        'RHBA-2018:1700-02')
])
def test_get_siblings_description(display_name, label, backward, expected):
    """Test the get_siblings_description function."""
    story_utils = BaseStoryManager()
    rv = story_utils.get_siblings_description(
        display_name, ContainerStoryManager().story_flow(label), backward)
    assert rv == expected
