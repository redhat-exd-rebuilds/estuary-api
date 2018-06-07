# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, StringProperty, ArrayProperty,
    DateTimeProperty, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode


class Advisory(EstuaryStructuredNode):
    """Definition of an Errata advisory in Neo4j."""

    actual_ship_date = DateTimeProperty()
    advisory_name = StringProperty(unique=True)
    content_types = ArrayProperty()
    created_at = DateTimeProperty()
    id_ = UniqueIdProperty(db_property='id')
    issue_date = DateTimeProperty()
    product_name = StringProperty()
    product_short_name = StringProperty()
    release_date = DateTimeProperty()
    security_impact = StringProperty()
    security_sla = DateTimeProperty()
    state = StringProperty()
    status_time = DateTimeProperty()
    synopsis = StringProperty()
    type_ = StringProperty(db_property='type')
    update_date = DateTimeProperty()
    updated_at = DateTimeProperty()
    assigned_to = RelationshipTo('.user.User', 'ASSIGNED_TO', cardinality=ZeroOrOne)
    attached_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'ATTACHED')
    attached_builds = RelationshipTo('.koji.KojiBuild', 'ATTACHED')
    package_owner = RelationshipTo('.user.User', 'PACKAGE_OWNED_BY', cardinality=ZeroOrOne)
    reporter = RelationshipTo('.user.User', 'REPORTED_BY', cardinality=ZeroOrOne)
    states = RelationshipFrom('AdvisoryState', 'STATE_OF')
    triggered_freshmaker_event = RelationshipFrom('.freshmaker.FreshmakerEvent', 'TRIGGERED_BY')


class AdvisoryState(EstuaryStructuredNode):
    """A representation of the states of an Errata advisory in Neo4j."""

    id_ = UniqueIdProperty(db_property='id')
    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()
    name = StringProperty(required=True)
    advisory = RelationshipTo('Advisory', 'STATE_OF', cardinality=ZeroOrOne)
    creator = RelationshipTo('.user.User', 'CREATED_BY', cardinality=ZeroOrOne)


class ContainerBuildAdvisory(Advisory):
    """Definition of an Errata advisory with container builds attached in Neo4j."""

    pass
