# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, StringProperty,
    ArrayProperty, DateTimeProperty)


class Advisory(StructuredNode):
    actual_ship_date = DateTimeProperty()
    advisory_name = StringProperty(unique=True, required=True)
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
    type_ = StringProperty(required=True, db_property='type')
    update_date = DateTimeProperty()
    updated_at = DateTimeProperty()
    assigned_to = RelationshipTo('.user.User', 'ASSIGNED_TO')
    attached_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED_TO')
    attached_builds = RelationshipTo('.koji.KojiBuild', 'RELATED_TO')
    # A normalized relationship name (same as reporters)
    owners = RelationshipTo('.user.User', 'OWNED_BY')
    package_owners = RelationshipTo('.user.User', 'PACKAGE_OWNED_BY')
    reporters = RelationshipTo('.user.User', 'REPORTED_BY')
    states = RelationshipTo('AdvisoryState', 'RELATED_TO')
    triggers_freshmaker_event = RelationshipTo('.freshmaker.FreshmakerEvent', 'TRIGGERS')
    triggers_container_builds = RelationshipTo('.freshmaker.ContainerBuilds', 'TRIGGERS')


class AdvisoryState(StructuredNode):
    id_ = UniqueIdProperty()
    created_at = DateTimeProperty()
    updated_at = DateTimeProperty()
    name = StringProperty(required=True)
    # Should only be one advisory but using plural since this is a list
    advisories = RelationshipTo('Advisory', 'RELATED_TO')
    owner = RelationshipTo('.user.User', 'OWNED_BY')
