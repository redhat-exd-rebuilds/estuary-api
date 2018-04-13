# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, StringProperty, DateTimeProperty)

from purview.models.base import PurviewStructuredNode


class DistGitRepo(PurviewStructuredNode):
    """Definition of a dist-git repo in Neo4j."""

    name = StringProperty(required=True)
    namespace = StringProperty(required=True)
    branches = RelationshipTo('DistGitBranch', 'CONTAINS')
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')


class DistGitBranch(PurviewStructuredNode):
    """Definition of a dist-git branch in Neo4j."""

    name = StringProperty(required=True)
    repo_name = StringProperty(required=True)
    repo_namespace = StringProperty(required=True)
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')
    repos = RelationshipTo('DistGitRepo', 'CONTAINED_BY')


class DistGitPush(PurviewStructuredNode):
    """Definition of a dist-git push in Neo4j."""

    id_ = UniqueIdProperty(db_property='id')
    push_date = DateTimeProperty(required=True)
    push_ip = StringProperty()
    branches = RelationshipTo('DistGitBranch', 'PUSHED_TO')
    commits = RelationshipTo('DistGitCommit', 'PUSHED')
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as pushers
    pushers = RelationshipTo('.user.User', 'PUSHED_BY')
    repos = RelationshipTo('DistGitRepo', 'PUSHED_TO')


class DistGitCommit(PurviewStructuredNode):
    """Definition of a dist-git commit in Neo4j."""

    author_date = DateTimeProperty()
    commit_date = DateTimeProperty()
    hash_ = UniqueIdProperty(db_property='hash')
    log_message = StringProperty()
    authors = RelationshipTo('.user.User', 'AUTHORED_BY')
    branches = RelationshipTo('DistGitBranch', 'CONTAINED_BY')
    children = RelationshipTo('.distgit.DistGitCommit', 'CHILD')
    committers = RelationshipTo('.user.User', 'OWNED_BY')
    koji_builds = RelationshipTo('.koji.KojiBuild', 'RELATED_TO')
    owners = RelationshipTo('.user.User', 'OWNED_BY')
    parents = RelationshipTo('.distgit.DistGitCommit', 'PARENT')
    pushes = RelationshipTo('DistGitPush', 'PUSHED_IN')
    related_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED_TO')
    repos = RelationshipTo('DistGitRepo', 'CONTAINED_BY')
    resolved_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RESOLVED')
    reverted_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'REVERTED')
