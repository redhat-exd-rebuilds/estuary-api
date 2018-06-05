# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, IntegerProperty, StringProperty,
    ZeroOrOne)

from purview.models.base import PurviewStructuredNode


class FreshmakerEvent(PurviewStructuredNode):
    """Definition of a Freshmaker event in Neo4j."""

    event_type_id = IntegerProperty(requried=True)
    id_ = UniqueIdProperty(db_property='id')
    message_id = StringProperty(unique=True, required=True)
    state = IntegerProperty()
    state_name = StringProperty()
    state_reason = StringProperty()
    triggered_by_advisory = RelationshipTo(
        '.errata.Advisory', 'TRIGGERED_BY', cardinality=ZeroOrOne)
    triggered_container_builds = RelationshipTo('.koji.ContainerKojiBuild', 'TRIGGERED')
    url = StringProperty(unique=True, required=True)
