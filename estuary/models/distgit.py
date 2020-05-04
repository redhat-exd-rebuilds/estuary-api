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
    commits = RelationshipTo('DistGitCommit', 'CONTAINS')
    contributors = RelationshipTo('.user.User', 'CONTRIBUTED_BY')

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return '{0}/{1}'.format(self.namespace, self.name)


class DistGitCommit(EstuaryStructuredNode):
    """Definition of a dist-git commit in Neo4j."""

    author_date = DateTimeProperty()
    commit_date = DateTimeProperty(index=True)
    hash_ = UniqueIdProperty(db_property='hash')
    log_message = StringProperty()
    author = RelationshipTo('.user.User', 'AUTHORED_BY', cardinality=ZeroOrOne)
    koji_builds = RelationshipFrom('.koji.KojiBuild', 'BUILT_FROM')
    related_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RELATED')
    repos = RelationshipFrom('DistGitRepo', 'CONTAINS')
    resolved_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'RESOLVED')
    reverted_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'REVERTED')

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return 'commit #{0}'.format(self.hash_[:7])

    @property
    def timeline_datetime(self):
        """Get the DateTime property used for the Estuary timeline."""
        return self.commit_date
