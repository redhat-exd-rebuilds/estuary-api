# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    StructuredNode, StringProperty, IntegerProperty, UniqueIdProperty,
    DateTimeProperty, FloatProperty, RelationshipTo)


class KojiBuild(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    tasks = RelationshipTo('KojiTask', 'TRIGGERS')
    owner = RelationshipTo('.user.User', 'OWNED_BY')
    tags = RelationshipTo('KojiTag', 'CONTAINED_BY')
    advisories = RelationshipTo('.errata.Advisory', 'RELATED_TO')
    epoch = StringProperty()
    state = IntegerProperty()
    creation_time = DateTimeProperty()
    start_time = DateTimeProperty()
    completion_time = DateTimeProperty()
    extra = StringProperty()
    name = StringProperty(required=True)
    version = StringProperty(required=True)
    release = StringProperty(required=True)


class KojiTask(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    builds = RelationshipTo('KojiBuild', 'TRIGGERED_BY')
    children = RelationshipTo('KojiTask', 'CHILD')
    parents = RelationshipTo('KojiTask', 'PARENT')
    owner = RelationshipTo('.user.User', 'OWNED_BY')
    weight = FloatProperty()
    create_time = DateTimeProperty(required=True)
    start_time = DateTimeProperty()
    completion_time = DateTimeProperty()
    state = IntegerProperty(required=True)
    priority = IntegerProperty()
    arch = StringProperty(required=True)
    method = StringProperty(required=True)


class KojiTag(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    builds = RelationshipTo('KojiBuild', 'CONTAINS')
    name = StringProperty(required=True)
