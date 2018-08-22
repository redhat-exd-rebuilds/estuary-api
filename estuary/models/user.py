# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import StringProperty, UniqueIdProperty, RelationshipFrom

from estuary.models.base import EstuaryStructuredNode


class User(EstuaryStructuredNode):
    """Definition of a generic user in Neo4j."""

    # These relationships can be reverse relationships of ones with cardinality set. So
    # these relationships should be treated as read-only or else cardinality will not be respected.
    advisories_assigned = RelationshipFrom('.errata.Advisory', 'ASSIGNED_TO')
    advisories_reported = RelationshipFrom('.errata.Advisory', 'REPORTED_BY')
    bugs_assigned = RelationshipFrom('.bugzilla.BugzillaBug', 'ASSIGNED_TO')
    bugs_qa_contact_for = RelationshipFrom('.bugzilla.BugzillaBug', 'QA_BY')
    bugs_reported = RelationshipFrom('.bugzilla.BugzillaBug', 'REPORTED_BY')
    distgit_authored_commits = RelationshipFrom('.distgit.DistGitCommit', 'AUTHORED_BY')
    distgit_branches = RelationshipFrom('.distgit.DistGitBranch', 'CONTRIBUTED_BY')
    distgit_repos = RelationshipFrom('.distgit.DistGitRepo', 'CONTRIBUTED_BY')
    email = StringProperty()
    koji_builds = RelationshipFrom('.koji.KojiBuild', 'OWNED_BY')
    name = StringProperty()
    username = UniqueIdProperty()

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return '{0}'.format(self.username)
