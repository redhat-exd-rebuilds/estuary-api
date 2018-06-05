# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, IntegerProperty, StringProperty,
    DateTimeProperty, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode


class FreshmakerEvent(EstuaryStructuredNode):
    """Definition of a Freshmaker event in Neo4j."""

    event_type_id = IntegerProperty(requried=True)
    id_ = UniqueIdProperty(db_property='id')
    message_id = StringProperty(unique=True, required=True)
    state = IntegerProperty()
    state_name = StringProperty()
    state_reason = StringProperty()
    triggered_by_advisory = RelationshipTo(
        '.errata.Advisory', 'TRIGGERED_BY', cardinality=ZeroOrOne)
    triggered_container_builds = RelationshipTo('ContainerBuild', 'TRIGGERED')
    url = StringProperty(unique=True, required=True)


class ContainerBuild(EstuaryStructuredNode):
    """Definition of a container build triggered by Freshmaker in Neo4j."""

    build_id = IntegerProperty(unique=True, required=True)
    dep_on = StringProperty()
    event_id = IntegerProperty(required=True)
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
    original_nvr = StringProperty()
    rebuilt_nvr = StringProperty()
    state = IntegerProperty()
    state_name = StringProperty()
    state_reason = StringProperty()
    time_completed = DateTimeProperty()
    time_submitted = DateTimeProperty(required=True)
    triggered_by_freshmaker_event = RelationshipFrom(
        'FreshmakerEvent', 'TRIGGERED', cardinality=ZeroOrOne)
    type_ = IntegerProperty(required=True, db_property='type')
    type_name = StringProperty(required=True)
    url = StringProperty(required=True)
