# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo)


class User(StructuredNode):
    username = UniqueIdProperty()
    koji_builds = RelationshipTo('.koji.KojiBuild', 'OWNS')
    koji_tasks = RelationshipTo('.koji.KojiTask', 'OWNS')
    bugzilla_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'OWNS')
    bugs_assigned_to = RelationshipTo('.bugzilla.BugzillaBug', 'ASSIGNED')
    bugs_reported_by = RelationshipTo('.bugzilla.BugzillaBug', 'REPORTED')
    bugs_qa_contact_for = RelationshipTo('.bugzilla.BugzillaBug', 'QA_CONTACT_FOR')
    distgit_authored_commits = RelationshipTo('.distgit.DistGitCommit', 'OWNS')
    distgit_committed_commits = RelationshipTo('.distgit.DistGitCommit', 'COMMITTED')
    distgit_pushes = RelationshipTo('.distgit.DistGitPush', 'PUSHED')
    distgit_branches = RelationshipTo('.distgit.DistGitBranch', 'CONTRIBUTED')
    distgit_repos = RelationshipTo('.distgit.DistGitRepo', 'CONTRIBUTED')
    name = StringProperty()
    email = StringProperty()
