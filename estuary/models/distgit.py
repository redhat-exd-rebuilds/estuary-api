# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    UniqueIdProperty, RelationshipTo, RelationshipFrom, StringProperty, DateTimeProperty,
    ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode


class DistGitRepo(EstuaryStructuredNode):
    """Definition of a dist-git repo in Neo4j."""

    name = StringProperty(required=True)
    namespace = StringProperty(required=True)
    branches = RelationshipTo('DistGitBranch', 'CONTAINS')
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')


class DistGitBranch(EstuaryStructuredNode):
    """Definition of a dist-git branch in Neo4j."""

    name = StringProperty(required=True)
    repo_name = StringProperty(required=True)
    repo_namespace = StringProperty(required=True)
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')
    repos = RelationshipFrom('DistGitRepo', 'CONTAINS')


class DistGitCommit(EstuaryStructuredNode):
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
    koji_builds = RelationshipFrom('.koji.KojiBuild', 'BUILT_FROM')
    parent = RelationshipTo('.distgit.DistGitCommit', 'PARENT', cardinality=ZeroOrOne)
    related_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED')
    repos = RelationshipFrom('DistGitRepo', 'CONTAINS')
    resolved_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RESOLVED')
    reverted_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'REVERTED')

    @property
    def display_label(self):
        """Get intuitive (human readable) display name for the node."""
        return 'commit #{0}'.format(self.hash_)
