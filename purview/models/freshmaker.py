# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo,
    IntegerProperty, StringProperty, DateTimeProperty)


class FreshmakerEvent(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    triggered_by_advisory = RelationshipTo(
        '.errata.Advisory', 'TRIGGERED_BY')
    triggers_container_builds = RelationshipTo('ContainerBuilds', 'TRIGGERS')
    event_type_id = IntegerProperty(requried=True)
    message_id = StringProperty(unique=True, required=True)
    search_key = StringProperty(unique=True, required=True)
    state = IntegerProperty(required=True)
    state_name = StringProperty(required=True)
    state_reason = StringProperty()
    url = StringProperty(unique=True, required=True)


class ContainerBuilds(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    triggered_by_advisory = RelationshipTo(
        '.errata.Advisory', 'TRIGGERED_BY')
    triggered_by_freshmaker_event = RelationshipTo(
        'FreshmakerEvent', 'TRIGGERED_BY')
    build_id = IntegerProperty(unique=True, required=True)
    dep_on = StringProperty()
    event_id = IntegerProperty(required=True)
    name = StringProperty(required=True)
    original_nvr = StringProperty(required=True)
    rebuilt_nvr = StringProperty(required=True)
    state = IntegerProperty(required=True)
    state_name = StringProperty(required=True)
    state_reason = StringProperty(required=True)
    time_completed = DateTimeProperty()
    time_submitted = DateTimeProperty(required=True)
    type_ = IntegerProperty(required=True, db_property='type')
    type_name = StringProperty(required=True)
    url = StringProperty(required=True)
