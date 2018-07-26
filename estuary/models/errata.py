# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import re

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, StringProperty, ArrayProperty,
    DateTimeProperty, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode
from estuary.error import ValidationError


class Advisory(EstuaryStructuredNode):
    """Definition of an Errata advisory in Neo4j."""

    actual_ship_date = DateTimeProperty()
    advisory_name = StringProperty(unique=True, index=True)
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
    update_date = DateTimeProperty()
    assigned_to = RelationshipTo('.user.User', 'ASSIGNED_TO', cardinality=ZeroOrOne)
    attached_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'ATTACHED')
    attached_builds = RelationshipTo('.koji.KojiBuild', 'ATTACHED')
    reporter = RelationshipTo('.user.User', 'REPORTED_BY', cardinality=ZeroOrOne)
    triggered_freshmaker_event = RelationshipFrom('.freshmaker.FreshmakerEvent', 'TRIGGERED_BY')

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return self.advisory_name

    @classmethod
    def find_or_none(cls, identifier):
        """
        Find the node using the supplied identifier.

        :param str identifier: the identifier to search the node by
        :return: the node or None
        :rtype: EstuaryStructuredNode or None
        """
        if re.match(r'^\d+$', identifier):
            # The identifier is an ID
            return cls.nodes.get_or_none(id_=identifier)
        elif re.match(r'^RH[A-Z]{2}-\d{4}:\d+-\d+$', identifier):
            # The identifier is a full advisory name
            return cls.nodes.get_or_none(advisory_name=identifier)
        elif re.match(r'^RH[A-Z]{2}-\d{4}:\d+$', identifier):
            # The identifier is most of the advisory name, so return the latest iteration of this
            # advisory
            return cls.nodes.filter(advisory_name__regex='^{0}-\d+$'.format(identifier))\
                .order_by('advisory_name').first_or_none()
        else:
            raise ValidationError('"{0}" is not a valid identifier'.format(identifier))


class ContainerAdvisory(Advisory):
    """Definition of an Errata advisory with container builds attached in Neo4j."""

    pass
