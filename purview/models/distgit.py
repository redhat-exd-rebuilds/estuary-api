# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, StringProperty, DateTimeProperty)

from purview.models.base import PurviewStructuredNode


class DistGitRepo(PurviewStructuredNode):
    name = StringProperty(required=True)
    namespace = StringProperty(required=True)
    branches = RelationshipTo('DistGitBranch', 'CONTAINS')
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')


class DistGitBranch(PurviewStructuredNode):
    name = StringProperty(required=True)
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')
    repos = RelationshipTo('DistGitRepo', 'CONTAINED_BY')


class DistGitPush(PurviewStructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    push_date = DateTimeProperty(required=True)
    push_ip = StringProperty()
    branches = RelationshipTo('DistGitBranch', 'PUSHED_TO')
    commits = RelationshipTo('DistGitCommit', 'PUSHED')
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as pushers
    pushers = RelationshipTo('.user.User', 'PUSHED_BY')
    repos = RelationshipTo('DistGitRepo', 'PUSHED_TO')


class DistGitCommit(PurviewStructuredNode):
    author_date = DateTimeProperty(required=True)
    commit_date = DateTimeProperty(required=True)
    log_message = StringProperty()
    sha = UniqueIdProperty()
    authors = RelationshipTo('.user.User', 'AUTHORED_BY')
    branches = RelationshipTo('DistGitBranch', 'CONTAINED_BY')
    committers = RelationshipTo('.user.User', 'OWNED_BY')
    koji_builds = RelationshipTo('.koji.KojiBuild', 'RELATED_TO')
    owners = RelationshipTo('.user.User', 'OWNED_BY')
    pushes = RelationshipTo('DistGitPush', 'PUSHED_IN')
    related_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED_TO')
    repos = RelationshipTo('DistGitRepo', 'CONTAINED_BY')
    resolved_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RESOLVED')
    reverted_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'REVERTED')
