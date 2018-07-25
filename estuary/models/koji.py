# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import re

from neomodel import (
    StringProperty, IntegerProperty, UniqueIdProperty, DateTimeProperty, FloatProperty,
    RelationshipTo, RelationshipFrom, ZeroOrOne)

from estuary.models.base import EstuaryStructuredNode
from estuary.error import ValidationError


class KojiBuild(EstuaryStructuredNode):
    """Definition of a Koji build in Neo4j."""

    advisories = RelationshipFrom('.errata.Advisory', 'ATTACHED')
    commit = RelationshipTo('.distgit.DistGitCommit', 'BUILT_FROM', cardinality=ZeroOrOne)
    completion_time = DateTimeProperty()
    creation_time = DateTimeProperty()
    epoch = StringProperty()
    extra = StringProperty()
    id_ = UniqueIdProperty(db_property='id')
    name = StringProperty(index=True)
    owner = RelationshipTo('.user.User', 'OWNED_BY', cardinality=ZeroOrOne)
    release = StringProperty(index=True)
    start_time = DateTimeProperty()
    state = IntegerProperty()
    tags = RelationshipFrom('KojiTag', 'CONTAINS')
    tasks = RelationshipFrom('KojiTask', 'TRIGGERED')
    version = StringProperty(index=True)

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return '{0}-{1}-{2}'.format(self.name, self.version, self.release)

    @classmethod
    def find_or_none(cls, identifier):
        """
        Find the node using the supplied identifier.

        :param str identifier: the identifier to search the node by
        :return: the node or None
        :rtype: EstuaryStructuredNode or None
        """
        uid = identifier
        if re.match(r'^\d+$', uid):
            # The identifier is an ID
            return cls.nodes.get_or_none(id_=uid)
        elif uid.endswith('.src.rpm'):
            # The identifer is likely an NVR with .src.rpm at the end, so strip that part of it
            # so it can be treated like a normal NVR
            uid = uid[:-8]

        if len(uid.rsplit('-', 2)) == 3:
            # The identifier looks like an NVR
            nvr = uid.rsplit('-', 2)
            return cls.nodes.get_or_none(name=nvr[0], version=nvr[1], release=nvr[2])

        raise ValidationError('"{0}" is not a valid identifier'.format(identifier))


class ContainerKojiBuild(KojiBuild):
    """A Neo4j definition of a build that represents a container build in Koji."""

    original_nvr = StringProperty()
    triggered_by_freshmaker_event = RelationshipFrom(
        '.freshmaker.FreshmakerEvent', 'TRIGGERED', cardinality=ZeroOrOne)


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
    name = StringProperty()
