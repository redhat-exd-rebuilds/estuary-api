# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

from neomodel import StructuredNode


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

        for key, value in self.__properties__.items():
            if isinstance(value, datetime):
                rv[key] = value.isoformat()

        return rv

    @property
    def serialized_all(self):
        """
        Returns a serialized form of the node with all its relationships
        :return: a dictionary
        """
        # Must be imported here to prevent a circular import
        from purview.models import all_models

        names_to_model = {model.__label__: model for model in all_models}
        # A set that will keep track of all properties on the node that weren't returned from Neo4j
        null_props = set()
        # A mapping of Neo4j relationship names to class property names per label (model class name)
        # e.g. {'Advisory': {'ASSIGNED': 'advisories_assigned', ...}}
        relationship_map = {}
        for prop_name, rel in self.__all_relationships__:
            label = rel.definition['node_class'].__label__
            neo4j_rel = rel.definition['relation_type']

            if not relationship_map.get(label):
                relationship_map[label] = {}
            relationship_map[label][neo4j_rel] = prop_name
            null_props.add(prop_name)

        # This variable will contain the current node as serialized + all relationships
        serialized = self.serialized
        # Get all the direct relationships
        results, _ = self.cypher('MATCH (a) WHERE id(a)={self} MATCH (a)-[r]->(all) RETURN r, all')
        for rel, node in results:
            for label in node.labels:
                if label in names_to_model:
                    node_model = names_to_model[label]
                    prop_name = relationship_map[label][rel.type]
                    break
            else:
                # This should never happen unless Neo4j returns labels that aren't associated with
                # classes in all_models
                RuntimeError('A StructuredNode couldn\'t be found from the labels: {0}'.format(
                    ', '.join(node.labels)))

            if not serialized.get(prop_name):
                serialized[prop_name] = []
                null_props.remove(prop_name)
            serialized[prop_name].append(node_model.inflate(node).serialized)

        # Neo4j won't return back relationships it doesn't know about, so just make them empty
        # lists so that the keys are always consistent
        for prop_name in null_props:
            serialized[prop_name] = []

        return serialized
