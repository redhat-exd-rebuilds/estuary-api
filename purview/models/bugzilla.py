# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, IntegerProperty, StringProperty,
    DateTimeProperty)


class BugzillaBug(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as the reporter
    assignees = RelationshipTo('.user.User', 'ASSIGNED_TO')
    reporters = RelationshipTo('.user.User', 'REPORTED_BY')
    qa_contacts = RelationshipTo('.user.User', 'QA_BY')
    severity = StringProperty(required=True)
    status = StringProperty(required=True)
    creation_time = DateTimeProperty(required=True)
    modified_time = DateTimeProperty(required=True)  # delta_ts
    priority = StringProperty(required=True)
    # Called product_name in case we want to use product as a relationship later on
    product_name = StringProperty(required=True)
    product_version = StringProperty(required=True)
    # This will always be "Red Hat" initially
    classification = StringProperty(required=True)
    resolution = StringProperty()
    target_milestone = StringProperty()
    votes = IntegerProperty()
    short_description = StringProperty()
