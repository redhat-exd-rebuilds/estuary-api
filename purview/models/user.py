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
    name = StringProperty()
    email = StringProperty()
