# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import re

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, IntegerProperty, StringProperty,
    DateTimeProperty, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode
from estuary.error import ValidationError


class BugzillaBug(EstuaryStructuredNode):
    """Definition of a Bugzilla bug in Neo4j."""

    assignee = RelationshipTo('.user.User', 'ASSIGNED_TO', cardinality=ZeroOrOne)
    attached_advisories = RelationshipFrom('.errata.Advisory', 'ATTACHED')
    classification = StringProperty()
    creation_time = DateTimeProperty()
    id_ = UniqueIdProperty(db_property='id')
    modified_time = DateTimeProperty()
    priority = StringProperty()
    # Called product_name in case we want to use product as a relationship later on
    product_name = StringProperty()
    product_version = StringProperty()
    qa_contact = RelationshipTo('.user.User', 'QA_BY', cardinality=ZeroOrOne)
    related_by_commits = RelationshipFrom('.distgit.DistGitCommit', 'RELATED')
    reporter = RelationshipTo('.user.User', 'REPORTED_BY', cardinality=ZeroOrOne)
    resolution = StringProperty()
    resolved_by_commits = RelationshipFrom('.distgit.DistGitCommit', 'RESOLVED')
    reverted_by_commits = RelationshipFrom('.distgit.DistGitCommit', 'REVERTED')
    severity = StringProperty()
    short_description = StringProperty()
    status = StringProperty()
    target_milestone = StringProperty()
    votes = IntegerProperty()

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return 'RHBZ#{0}'.format(self.id_)

    @classmethod
    def find_or_none(cls, identifier):
        """
        Find the node using the supplied identifier.

        :param str identifier: the identifier to search the node by
        :return: the node or None
        :rtype: EstuaryStructuredNode or None
        """
        uid = identifier
        if uid.lower().startswith('rhbz'):
            uid = uid[4:]
        if uid.startswith('#'):
            uid = uid[1:]

        # If we are left with something other than digits, then it is an invalid identifier
        if not re.match(r'^\d+$', uid):
            raise ValidationError('"{0}" is not a valid identifier'.format(identifier))

        return cls.nodes.get_or_none(id_=uid)
