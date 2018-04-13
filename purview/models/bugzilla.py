# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, IntegerProperty, StringProperty, DateTimeProperty)

from purview.models.base import PurviewStructuredNode


class BugzillaBug(PurviewStructuredNode):
    """Definition of a Bugzilla bug in Neo4j."""

    assignees = RelationshipTo('.user.User', 'ASSIGNED_TO')
    attached_advisories = RelationshipTo('.errata.Advisory', 'RELATED_TO')
    # This will always be "Red Hat" initially
    classification = StringProperty()
    creation_time = DateTimeProperty()
    id_ = UniqueIdProperty(db_property='id')
    modified_time = DateTimeProperty()  # delta_ts
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as the reporter
    priority = StringProperty()
    # Called product_name in case we want to use product as a relationship later on
    product_name = StringProperty()
    product_version = StringProperty()
    qa_contacts = RelationshipTo('.user.User', 'QA_BY')
    related_by_commits = RelationshipTo('.distgit.DistGitCommit', 'RELATED_TO')
    reporters = RelationshipTo('.user.User', 'REPORTED_BY')
    resolution = StringProperty()
    resolved_by_commits = RelationshipTo('.distgit.DistGitCommit', 'RESOLVED_BY')
    reverted_by_commits = RelationshipTo('.distgit.DistGitCommit', 'REVERTED_BY')
    severity = StringProperty()
    short_description = StringProperty()
    status = StringProperty()
    target_milestone = StringProperty()
    votes = IntegerProperty()
