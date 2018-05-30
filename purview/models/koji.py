# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    StringProperty, IntegerProperty, UniqueIdProperty, DateTimeProperty, FloatProperty,
    RelationshipTo, RelationshipFrom, ZeroOrOne)

from purview.models.base import PurviewStructuredNode


class KojiBuild(PurviewStructuredNode):
    """Definition of a Koji build in Neo4j."""

    advisories = RelationshipFrom('.errata.Advisory', 'ATTACHED')
    commit = RelationshipTo('.distgit.DistGitCommit', 'BUILT_FROM', cardinality=ZeroOrOne)
    completion_time = DateTimeProperty()
    creation_time = DateTimeProperty()
    epoch = StringProperty()
    extra = StringProperty()
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty()
    owner = RelationshipTo('.user.User', 'OWNED_BY', cardinality=ZeroOrOne)
    release = StringProperty()
    start_time = DateTimeProperty()
    state = IntegerProperty()
    tags = RelationshipFrom('KojiTag', 'CONTAINS')
    tasks = RelationshipFrom('KojiTask', 'TRIGGERED')
    triggered_by_freshmaker_event = RelationshipFrom(
        '.freshmaker.FreshmakerEvent', 'TRIGGERED', cardinality=ZeroOrOne)
    version = StringProperty()


class ContainerKojiBuild(KojiBuild):
    """Creating another label for KojiBuild"""
    pass


class KojiTask(PurviewStructuredNode):
    """Definition of a Koji task in Neo4j."""

    arch = StringProperty(required=True)
    builds = RelationshipTo('KojiBuild', 'TRIGGERED')
    # Cardinality is enforced on the `parent` property, so the `children` property should be
    # treated as read-only
    children = RelationshipFrom('KojiTask', 'PARENT')
    completion_time = DateTimeProperty()
    create_time = DateTimeProperty(required=True)
    id_ = UniqueIdProperty(db_property='id')
    method = StringProperty(required=True)
    owner = RelationshipTo('.user.User', 'OWNED_BY')
    parent = RelationshipTo('KojiTask', 'PARENT', cardinality=ZeroOrOne)
    priority = IntegerProperty()
    start_time = DateTimeProperty()
    state = IntegerProperty()
    weight = FloatProperty()


class KojiTag(PurviewStructuredNode):
    """Definition of a Koji tag in Neo4j."""

    builds = RelationshipTo('KojiBuild', 'CONTAINS')
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
