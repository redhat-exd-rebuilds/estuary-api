# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import pytest
from neomodel import UniqueIdProperty, One, RelationshipTo

from estuary.models.base import EstuaryStructuredNode
from estuary.models.errata import Advisory
from estuary.models.user import User
from estuary.models.bugzilla import BugzillaBug


def test_conditional_connect_zero_or_one():
    """Test EstuaryStructuredNode.conditional_connect on a ZerorOrOne relationship."""
    adv = Advisory(id_='12345', advisory_name='RHBA-2017:27760-01').save()
    tbrady = User(username='tbrady').save()
    thanks = User(username='thanks').save()

    assert len(adv.assigned_to) == 0
    EstuaryStructuredNode.conditional_connect(adv.assigned_to, tbrady)
    assert tbrady in adv.assigned_to
    assert len(adv.assigned_to) == 1

    EstuaryStructuredNode.conditional_connect(adv.assigned_to, thanks)
    assert tbrady not in adv.assigned_to
    assert thanks in adv.assigned_to
    assert len(adv.assigned_to) == 1


def test_conditional_connect_zero_or_more():
    """Test EstuaryStructuredNode.conditional_connect on a ZeroOrMore relationship."""
    adv = Advisory(id_='12345', advisory_name='RHBA-2017:27760-01').save()
    bug = BugzillaBug(id_='2345').save()
    bug_two = BugzillaBug(id_='3456').save()

    assert len(adv.attached_bugs) == 0
    EstuaryStructuredNode.conditional_connect(adv.attached_bugs, bug)
    assert bug in adv.attached_bugs
    assert len(adv.attached_bugs) == 1

    EstuaryStructuredNode.conditional_connect(adv.attached_bugs, bug_two)
    assert bug in adv.attached_bugs
    assert bug_two in adv.attached_bugs
    assert len(adv.attached_bugs) == 2


def test_conditional_connect_one():
    """Test EstuaryStructuredNode.conditional_connect on a One relationship."""
    class TestModel(EstuaryStructuredNode):
        id_ = UniqueIdProperty(db_property='id')
        owner = RelationshipTo('estuary.models.user.User', 'OWNS', cardinality=One)

    tbrady = User(username='tbrady').save()
    thanks = User(username='thanks').save()
    test = TestModel(id_='12345').save()
    test.owner.connect(tbrady)
    with pytest.raises(NotImplementedError)as exc_info:
        EstuaryStructuredNode.conditional_connect(test.owner, thanks)
    assert 'conditional_connect doesn\'t support cardinality of one' == str(exc_info.value)
