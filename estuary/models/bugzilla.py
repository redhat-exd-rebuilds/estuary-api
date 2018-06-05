# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, IntegerProperty, StringProperty,
    DateTimeProperty, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode


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
