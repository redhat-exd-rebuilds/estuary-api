# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    StringProperty, IntegerProperty, UniqueIdProperty, DateTimeProperty, FloatProperty,
    RelationshipTo)

from purview.models.base import PurviewStructuredNode


class KojiBuild(PurviewStructuredNode):
    advisories = RelationshipTo('.errata.Advisory', 'RELATED_TO')
    commits = RelationshipTo('.distgit.DistGitCommit', 'RELATED_TO')
    completion_time = DateTimeProperty()
    creation_time = DateTimeProperty()
    epoch = StringProperty()
    extra = StringProperty()
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
    owner = RelationshipTo('.user.User', 'OWNED_BY')
    release = StringProperty(required=True)
    start_time = DateTimeProperty()
    state = IntegerProperty()
    tags = RelationshipTo('KojiTag', 'CONTAINED_BY')
    tasks = RelationshipTo('KojiTask', 'TRIGGERS')
    version = StringProperty(required=True)


class KojiTask(PurviewStructuredNode):
    arch = StringProperty(required=True)
    builds = RelationshipTo('KojiBuild', 'TRIGGERED_BY')
    children = RelationshipTo('KojiTask', 'CHILD')
    completion_time = DateTimeProperty()
    create_time = DateTimeProperty(required=True)
    id_ = UniqueIdProperty(db_property='id')
    method = StringProperty(required=True)
    owner = RelationshipTo('.user.User', 'OWNED_BY')
    parents = RelationshipTo('KojiTask', 'PARENT')
    priority = IntegerProperty()
    start_time = DateTimeProperty()
    state = IntegerProperty(required=True)
    weight = FloatProperty()


class KojiTag(PurviewStructuredNode):
    builds = RelationshipTo('KojiBuild', 'CONTAINS')
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
