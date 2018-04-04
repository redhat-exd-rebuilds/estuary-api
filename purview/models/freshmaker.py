# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo,
    IntegerProperty, StringProperty, DateTimeProperty)


class FreshmakerEvent(StructuredNode):
    event_type_id = IntegerProperty(requried=True)
    id_ = UniqueIdProperty(db_property='id')
    message_id = StringProperty(unique=True, required=True)
    state = IntegerProperty(required=True)
    state_name = StringProperty(required=True)
    state_reason = StringProperty()
    triggered_by_advisory = RelationshipTo(
        '.errata.Advisory', 'TRIGGERED_BY')
    triggers_container_builds = RelationshipTo('ContainerBuilds', 'TRIGGERS')
    url = StringProperty(unique=True, required=True)


class ContainerBuilds(StructuredNode):
    build_id = IntegerProperty(unique=True, required=True)
    dep_on = StringProperty()
    event_id = IntegerProperty(required=True)
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
    original_nvr = StringProperty(required=True)
    rebuilt_nvr = StringProperty(required=True)
    state = IntegerProperty(required=True)
    state_name = StringProperty(required=True)
    state_reason = StringProperty()
    time_completed = DateTimeProperty()
    time_submitted = DateTimeProperty(required=True)
    triggered_by_freshmaker_event = RelationshipTo(
        'FreshmakerEvent', 'TRIGGERED_BY')
    type_ = IntegerProperty(required=True, db_property='type')
    type_name = StringProperty(required=True)
    url = StringProperty(required=True)
