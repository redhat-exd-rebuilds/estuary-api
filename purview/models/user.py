# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo)


class User(StructuredNode):
    username = UniqueIdProperty()
    owns_builds = RelationshipTo('.koji.KojiBuild', 'OWNS')
    owns_tasks = RelationshipTo('.koji.KojiTask', 'OWNS')
    name = StringProperty()
    email = StringProperty()
