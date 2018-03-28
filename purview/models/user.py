# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo)


class User(StructuredNode):
    email = StringProperty()
    name = StringProperty()
    username = UniqueIdProperty()
    bugs_assigned_to = RelationshipTo('.bugzilla.BugzillaBug', 'ASSIGNED')
    bugs_reported_by = RelationshipTo('.bugzilla.BugzillaBug', 'REPORTED')
    bugs_qa_contact_for = RelationshipTo('.bugzilla.BugzillaBug', 'QA_CONTACT_FOR')
    bugzilla_bugs = RelationshipTo('.bugzilla.BugzillaBug', 'OWNS')
    distgit_authored_commits = RelationshipTo('.distgit.DistGitCommit', 'OWNS')
    distgit_branches = RelationshipTo('.distgit.DistGitBranch', 'CONTRIBUTED')
    distgit_committed_commits = RelationshipTo('.distgit.DistGitCommit', 'COMMITTED')
    distgit_pushes = RelationshipTo('.distgit.DistGitPush', 'PUSHED')
    distgit_repos = RelationshipTo('.distgit.DistGitRepo', 'CONTRIBUTED')
    koji_builds = RelationshipTo('.koji.KojiBuild', 'OWNS')
    koji_tasks = RelationshipTo('.koji.KojiTask', 'OWNS')
