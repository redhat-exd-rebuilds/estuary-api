# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, StringProperty, IntegerProperty, UniqueIdProperty,
    BooleanProperty, DateTimeProperty, FloatProperty, RelationshipTo)


class KojiBuild(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    tasks = RelationshipTo('KojiTask', 'TRIGGERS')
    owner = RelationshipTo('.user.User', 'OWNED_BY')
    epoch = StringProperty()
    state = IntegerProperty(required=True)
    creation_time = DateTimeProperty(required=True)
    start_time = DateTimeProperty()
    completion_time = DateTimeProperty()
    extra = StringProperty()
    name = StringProperty(required=True)
    version = StringProperty(required=True)
    release = StringProperty(required=True)
    nvr = StringProperty(required=True)


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
    scratch = BooleanProperty()
