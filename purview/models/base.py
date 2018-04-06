# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import StructuredNode
from neomodel.relationship_manager import RelationshipDefinition


class PurviewStructuredNode(StructuredNode):
    __abstract_node__ = True

    @property
    def serialized(self):
        rv = self.__properties__
        # Remove the Neo4j internal ID
        del rv['id']
        # "id_" is actually the node's ID from the source
        if 'id_' in rv:
            # Rename as "id" for clarity
            rv['id'] = rv['id_']
            del rv['id_']

        # Imported here to prevent a circular import
        from purview.models.user import User

        for prop, prop_def in self.defined_properties().items():
            if isinstance(prop_def, RelationshipDefinition) and \
                    prop_def.definition['node_class'] == User:
                prop_obj = getattr(self, prop)
                # For now all user relationships will be lists since we don't know if they are
                # one-to-one. To change this, we'd need cardinality.
                rv[prop] = [user.username for user in prop_obj.all()]

        return rv
