# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, StringProperty,
    DateTimeProperty)


class DistGitRepo(StructuredNode):
    name = StringProperty(required=True)
    namespace = StringProperty(required=True)
    branches = RelationshipTo('DistGitBranch', 'CONTAINS')
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')


class DistGitBranch(StructuredNode):
    name = StringProperty(required=True)
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')
    repos = RelationshipTo('DistGitRepo', 'CONTAINED_BY')


class DistGitPush(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    push_date = DateTimeProperty(required=True)
    push_ip = StringProperty()
    branches = RelationshipTo('DistGitBranch', 'PUSHED_TO')
    commits = RelationshipTo('DistGitCommit', 'PUSHED')
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as pushers
    pushers = RelationshipTo('.user.User', 'PUSHED_BY')
    repos = RelationshipTo('DistGitRepo', 'PUSHED_TO')


class DistGitCommit(StructuredNode):
    author_date = DateTimeProperty(required=True)
    commit_date = DateTimeProperty(required=True)
    id_ = UniqueIdProperty(db_property='id')
    log_message = StringProperty()
    sha = StringProperty(required=True)
    authors = RelationshipTo('.user.User', 'AUTHORED_BY')
    branches = RelationshipTo('DistGitBranch', 'CONTAINED_BY')
    committers = RelationshipTo('.user.User', 'OWNED_BY')
    owners = RelationshipTo('.user.User', 'OWNED_BY')
    pushes = RelationshipTo('DistGitPush', 'PUSHED_IN')
    related_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED_TO')
    repos = RelationshipTo('DistGitRepo', 'CONTAINED_BY')
    resolved_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RESOLVED')
    reverted_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'REVERTED')
