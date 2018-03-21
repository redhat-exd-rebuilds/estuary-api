# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, IntegerProperty,
    StringProperty, BooleanProperty, ArrayProperty)


class Advisory(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    triggers_freshmaker_event = RelationshipTo(
        '.freshmaker.FreshmakerEvent', 'TRIGGERS')
    triggers_container_builds = RelationshipTo(
        '.freshmaker.ContainerBuilds', 'TRIGGERS')
    advisory_name = StringProperty(unique=True, required=True)
    status = StringProperty(required=True)
    # product = Property() # a dict that should be broken out
    text_only = BooleanProperty()
    # people = Property() # a dict that should be broken out
    content_types = ArrayProperty()
    pushcount = IntegerProperty()
    synopsis = StringProperty(required=True)
    respin_count = IntegerProperty()
    security_impact = StringProperty(required=True)
    # flags = Property() # a dict that should be broken out
    # release = Property() # a dict that should be broken out
    # timestamps = Property() # a dict that should be broken out
    # content = Property() # a dict that should be broken out
    type_ = StringProperty(required=True, db_property='type')
    revision = IntegerProperty(require=True)
