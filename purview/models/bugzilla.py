# SPDX-License-Identifier: GPL-3.0+

from neomodel import StructuredNode, UniqueIdProperty, RelationshipTo


class BugzillaBug(StructuredNode):
    id_ = UniqueIdProperty(db_property='id')
    # The three possible relationships to commits in GitBZ
    resolved_by = RelationshipTo('.distgit.DistgitCommit', 'RESOLVED_BY')
    reverted_by = RelationshipTo('.distgit.DistgitCommit', 'REVERTED_BY')
    relates_to = RelationshipTo('.distgit.DistgitCommit', 'RELATES_TO')
