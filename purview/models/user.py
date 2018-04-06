# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import StringProperty, UniqueIdProperty, RelationshipTo

from purview.models.base import PurviewStructuredNode


class User(PurviewStructuredNode):
    _default_property = 'username'
    # A normalized relationship (same as advisories_reported_by)
    advisories = RelationshipTo('.errata.Advisory', 'OWNS')
    advisories_assigned = RelationshipTo('.errata.Advisory', 'ASSIGNED')
    advisories_package_owner = RelationshipTo('.errata.Advisory', 'PACKAGE_OWNED')
    advisories_reported = RelationshipTo('.errata.Advisory', 'REPORTED')
    advisories_state_owner = RelationshipTo('.errata.AdvisoryState', 'OWNS')
    bugs_assigned_to = RelationshipTo('.bugzilla.BugzillaBug', 'ASSIGNED')
    bugs_qa_contact_for = RelationshipTo('.bugzilla.BugzillaBug', 'QA_CONTACT_FOR')
    bugs_reported_by = RelationshipTo('.bugzilla.BugzillaBug', 'REPORTED')
    bugzilla_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'OWNS')
    distgit_authored_commits = RelationshipTo('.distgit.DistGitCommit', 'OWNS')
    distgit_branches = RelationshipTo('.distgit.DistGitBranch', 'CONTRIBUTED')
    distgit_committed_commits = RelationshipTo('.distgit.DistGitCommit', 'COMMITTED')
    distgit_pushes = RelationshipTo('.distgit.DistGitPush', 'PUSHED')
    distgit_repos = RelationshipTo('.distgit.DistGitRepo', 'CONTRIBUTED')
    email = StringProperty()
    koji_builds = RelationshipTo('.koji.KojiBuild', 'OWNS')
    koji_tasks = RelationshipTo('.koji.KojiTask', 'OWNS')
    name = StringProperty()
    username = UniqueIdProperty()
