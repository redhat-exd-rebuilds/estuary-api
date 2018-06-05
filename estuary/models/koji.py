# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import (
    StringProperty, IntegerProperty, UniqueIdProperty, DateTimeProperty, FloatProperty,
    RelationshipTo, RelationshipFrom, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode


class KojiBuild(EstuaryStructuredNode):
    """Definition of a Koji build in Neo4j."""

    advisories = RelationshipFrom('.errata.Advisory', 'ATTACHED')
    commit = RelationshipTo('.distgit.DistGitCommit', 'BUILT_FROM', cardinality=ZeroOrOne)
    completion_time = DateTimeProperty()
    creation_time = DateTimeProperty()
    epoch = StringProperty()
    extra = StringProperty()
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
    owner = RelationshipTo('.user.User', 'OWNED_BY', cardinality=ZeroOrOne)
    release = StringProperty(required=True)
    start_time = DateTimeProperty()
    state = IntegerProperty()
    tags = RelationshipFrom('KojiTag', 'CONTAINS')
    tasks = RelationshipFrom('KojiTask', 'TRIGGERED')
    version = StringProperty(required=True)


class KojiTask(EstuaryStructuredNode):
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


class KojiTag(EstuaryStructuredNode):
    """Definition of a Koji tag in Neo4j."""

    builds = RelationshipTo('KojiBuild', 'CONTAINS')
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(required=True)
