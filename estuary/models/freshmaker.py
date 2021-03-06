# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (DateTimeProperty, IntegerProperty, RelationshipFrom,
                      RelationshipTo, StringProperty, UniqueIdProperty,
                      ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode


class FreshmakerEvent(EstuaryStructuredNode):
    """Definition of a Freshmaker event in Neo4j."""

    id_ = UniqueIdProperty(db_property='id')
    state_name = StringProperty()
    state_reason = StringProperty()
    time_created = DateTimeProperty()
    time_done = DateTimeProperty()
    triggered_by_advisory = RelationshipTo(
        '.errata.Advisory', 'TRIGGERED_BY', cardinality=ZeroOrOne)
    successful_koji_builds = RelationshipTo('.koji.ContainerKojiBuild', 'TRIGGERED')
    requested_builds = RelationshipTo('.FreshmakerBuild', 'TRIGGERED')

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return 'Freshmaker event {0}'.format(self.id_)

    @property
    def timeline_datetime(self):
        """Get the DateTime property used for the Estuary timeline."""
        return self.time_created


class FreshmakerBuild(EstuaryStructuredNode):
    """Definition of a Freshmaker build in Neo4j."""

    id_ = UniqueIdProperty(db_property='id')
    build_id = IntegerProperty()
    dep_on = StringProperty()
    name = StringProperty()
    original_nvr = StringProperty()
    rebuilt_nvr = StringProperty()
    state_name = StringProperty()
    state_reason = StringProperty()
    time_completed = DateTimeProperty()
    time_submitted = DateTimeProperty()
    type_name = StringProperty()
    koji_builds = RelationshipTo('.koji.ContainerKojiBuild', 'TRIGGERED_BY', cardinality=ZeroOrOne)
    event = RelationshipFrom('.FreshmakerEvent', 'TRIGGERED', cardinality=ZeroOrOne)

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return 'Freshmaker build {0}'.format(self.id_)
