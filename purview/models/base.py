# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

from neomodel import StructuredNode

from purview.utils.general import inflate_node


class PurviewStructuredNode(StructuredNode):
    """Base class for Purview Neo4j models."""

    __abstract_node__ = True

    @property
    def serialized(self):
        """
        Convert a model to serialized form.

        :return: a serialized form of the node
        :rtype: dictionary
        """
        rv = {}
        for key, value in self.__properties__.items():
            # id is the internal Neo4j ID that we don't want to display to the user
            if key == 'id':
                continue
            actual_key = getattr(self.__class__, key).db_property or key

            if isinstance(value, datetime):
                rv[actual_key] = value.isoformat()
            else:
                rv[actual_key] = value

        return rv

    @property
    def serialized_all(self):
        """
        Generate a serialized form of the node that includes all its relationships.

        :return: a serialized form of the node with relationships
        :rtype: dictionary
        :raises RuntimeError: if the label of a Neo4j node can't be mapped back to a neomodel class
        """
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
            inflated_node = inflate_node(node)
            prop_name = relationship_map[inflated_node.__label__][rel.type]
            if not serialized.get(prop_name):
                serialized[prop_name] = []
                null_props.remove(prop_name)
            serialized[prop_name].append(inflated_node.serialized)

        # Neo4j won't return back relationships it doesn't know about, so just make them empty
        # lists so that the keys are always consistent
        for prop_name in null_props:
            serialized[prop_name] = []

        return serialized
