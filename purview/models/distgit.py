# SPDX-License-Identifier: GPL-3.0+

from neomodel import (
    StructuredNode, UniqueIdProperty, RelationshipTo, StringProperty,
    DateTimeProperty)


class DistgitCommit(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')  # commit_id
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as author
    authors = RelationshipTo('.user.User', 'AUTHORED_BY')  # author_id
    committers = RelationshipTo('.user.User', 'OWNED_BY')
    pushes = RelationshipTo('DistgitPush', 'PUSHED_IN')
    author_date = DateTimeProperty(required=True)
    commit_date = DateTimeProperty(required=True)
    sha = StringProperty(required=True)
    log_message = StringProperty()


class DistgitPush(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')  # push_id
    owners = RelationshipTo('.user.User', 'OWNED_BY')  # same as pusher
    pushers = RelationshipTo('.user.User', 'OWNED_BY')  # pusher
    commits = RelationshipTo('DistgitCommit', 'PUSHES')  # commit_id
    push_date = DateTimeProperty(required=True)
    push_ip = StringProperty()
    module = StringProperty(required=True)
    ref = StringProperty(required=True)
