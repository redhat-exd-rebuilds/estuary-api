# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, StringProperty, DateTimeProperty,
    ZeroOrOne)

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
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')
    pushes = RelationshipTo('DistGitPush', 'CONTAINS')
    repos = RelationshipFrom('DistGitRepo', 'CONTAINS')


class DistGitPush(PurviewStructuredNode):
    """Definition of a dist-git push in Neo4j."""

    id_ = UniqueIdProperty(db_property='id')
    push_date = DateTimeProperty(required=True)
    push_ip = StringProperty()
    branch = RelationshipFrom('DistGitBranch', 'CONTAINS', cardinality=ZeroOrOne)
    commits = RelationshipTo('DistGitCommit', 'PUSHED')
    pusher = RelationshipTo('.user.User', 'PUSHED_BY', cardinality=ZeroOrOne)
    repo = RelationshipFrom('DistGitRepo', 'CONTAINS', cardinality=ZeroOrOne)


class DistGitCommit(PurviewStructuredNode):
    """Definition of a dist-git commit in Neo4j."""

    author_date = DateTimeProperty()
    commit_date = DateTimeProperty()
    hash_ = UniqueIdProperty(db_property='hash')
    log_message = StringProperty()
    author = RelationshipTo('.user.User', 'AUTHORED_BY', cardinality=ZeroOrOne)
    branches = RelationshipFrom('DistGitBranch', 'CONTAINS')
    # Cardinality is enforced on the `parent` property, so the `children` property should be
    # treated as read-only
    children = RelationshipFrom('.distgit.DistGitCommit', 'PARENT')
    committer = RelationshipTo('.user.User', 'COMMITTED_BY', cardinality=ZeroOrOne)
    koji_builds = RelationshipFrom('.koji.KojiBuild', 'BUILT_FROM')
    parent = RelationshipTo('.distgit.DistGitCommit', 'PARENT', cardinality=ZeroOrOne)
    pushes = RelationshipFrom('DistGitPush', 'CONTAINS')
    related_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED')
    repos = RelationshipFrom('DistGitRepo', 'CONTAINS')
    resolved_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RESOLVED')
    reverted_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'REVERTED')
