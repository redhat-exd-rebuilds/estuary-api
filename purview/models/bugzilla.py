# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, IntegerProperty, StringProperty,
    DateTimeProperty)


class BugzillaBug(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as the reporter
    assignees = RelationshipTo('.user.User', 'ASSIGNED_TO')
    reporters = RelationshipTo('.user.User', 'REPORTED_BY')
    qa_contacts = RelationshipTo('.user.User', 'QA_BY')
    related_by_commits = RelationshipTo('.distgit.DistGitCommit', 'RELATED_TO')
    resolved_by_commits = RelationshipTo('.distgit.DistGitCommit', 'RESOLVED_BY')
    reverted_by_commits = RelationshipTo('.distgit.DistGitCommit', 'REVERTED_BY')
    attached_advisories = RelationshipTo('.errata.Advisory', 'RELATED_TO')
    severity = StringProperty()
    status = StringProperty()
    creation_time = DateTimeProperty()
    modified_time = DateTimeProperty()  # delta_ts
    priority = StringProperty()
    # Called product_name in case we want to use product as a relationship later on
    product_name = StringProperty()
    product_version = StringProperty()
    # This will always be "Red Hat" initially
    classification = StringProperty()
    resolution = StringProperty()
    target_milestone = StringProperty()
    votes = IntegerProperty()
    short_description = StringProperty()
