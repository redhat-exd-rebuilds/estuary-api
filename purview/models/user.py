# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo)


class User(StructuredNode):
    username = UniqueIdProperty()
    koji_builds = RelationshipTo('.koji.KojiBuild', 'OWNS')
    koji_tasks = RelationshipTo('.koji.KojiTask', 'OWNS')
    name = StringProperty()
    email = StringProperty()
