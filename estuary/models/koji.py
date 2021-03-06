# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import re

from neomodel import (BooleanProperty, DateTimeProperty, IntegerProperty,
                      RelationshipFrom, RelationshipTo, StringProperty,
                      UniqueIdProperty, ZeroOrOne)

from estuary.error import ValidationError
from estuary.models.base import EstuaryStructuredNode
from estuary.models.errata import Advisory


class KojiBuild(EstuaryStructuredNode):
    """Definition of a Koji build in Neo4j."""

    advisories = RelationshipFrom('.errata.Advisory', 'ATTACHED', model=Advisory.BuildAttachedRel)
    commit = RelationshipTo('.distgit.DistGitCommit', 'BUILT_FROM', cardinality=ZeroOrOne)
    completion_time = DateTimeProperty(index=True)
    creation_time = DateTimeProperty()
    epoch = StringProperty()
    id_ = UniqueIdProperty(db_property='id')
    module_builds = RelationshipFrom('ModuleKojiBuild', 'ATTACHED')
    name = StringProperty(index=True)
    owner = RelationshipTo('.user.User', 'OWNED_BY', cardinality=ZeroOrOne)
    release = StringProperty(index=True)
    start_time = DateTimeProperty()
    state = IntegerProperty()
    version = StringProperty(index=True)

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        return '{0}-{1}-{2}'.format(self.name, self.version, self.release)

    @property
    def timeline_datetime(self):
        """Get the DateTime property used for the Estuary timeline."""
        return self.creation_time

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
    operator = BooleanProperty(default=False)


class ModuleKojiBuild(KojiBuild):
    """A Neo4j definition of a build that represents a module build in Koji."""

    components = RelationshipTo('KojiBuild', 'ATTACHED')
    context = StringProperty()
    mbs_id = IntegerProperty()
    module_name = StringProperty()
    module_stream = StringProperty()
    module_version = StringProperty()
