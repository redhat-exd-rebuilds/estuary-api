# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

from neomodel import StructuredNode, One, ZeroOrOne, OUTGOING, INCOMING, EITHER, UniqueIdProperty

from estuary import log
from estuary.utils.general import inflate_node


class EstuaryStructuredNode(StructuredNode):
    """Base class for Estuary Neo4j models."""

    __abstract_node__ = True

    @property
    def display_name(self):
        """Get intuitive (human readable) display name for the node."""
        raise NotImplemented('The display_name method is not defined')

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
        # Avoid circular imports
        from estuary.models import models_inheritance
        # A set that will keep track of all properties on the node that weren't returned from Neo4j
        null_properties = set()
        # A mapping of Neo4j relationship names in the format of:
        # {
        #     node_label: {
        #         relationship_name: {direction: (property_name, cardinality_class) ...},
        #     }
        # }
        relationship_map = {}
        for property_name, relationship in self.__all_relationships__:
            node_label = relationship.definition['node_class'].__label__
            relationship_name = relationship.definition['relation_type']
            for label in models_inheritance[node_label]:
                if label not in relationship_map:
                    relationship_map[label] = {}

                relationship_direction = relationship.definition['direction']
                if relationship_direction == EITHER:
                    # The direction can be coming from either direction, so map both
                    properties = {
                        INCOMING: (property_name, relationship.manager),
                        OUTGOING: (property_name, relationship.manager),
                    }
                else:
                    properties = {relationship_direction: (property_name, relationship.manager)}

                if relationship_name not in relationship_map[label]:
                    relationship_map[label][relationship_name] = properties
                else:
                    relationship_map[label][relationship_name].update(properties)
                null_properties.add(property_name)

        # This variable will contain the current node as serialized + all relationships
        serialized = self.serialized
        # Get all the direct relationships in both directions
        results, _ = self.cypher('MATCH (a) WHERE id(a)={self} MATCH (a)-[r]-(all) RETURN r, all')
        for relationship, node in results:
            # If the starting node in the relationship is the same as the node being serialized,
            # we know that the relationship is outgoing
            if relationship.start == self.id:
                direction = OUTGOING
            else:
                direction = INCOMING

            # Convert the Neo4j result into a model object
            inflated_node = inflate_node(node)
            try:
                property_name, cardinality_class = \
                    relationship_map[inflated_node.__label__][relationship.type][direction]
            except KeyError:
                if direction == OUTGOING:
                    direction_text = 'outgoing'
                else:
                    direction_text = 'incoming'
                log.warn(
                    'An {0} {1} relationship of {2!r} with {3!r} is not mapped in the models and '
                    'will be ignored'.format(direction_text, relationship.type, self, inflate_node))
                continue

            if not serialized.get(property_name):
                null_properties.remove(property_name)

            if cardinality_class in (One, ZeroOrOne):
                serialized[property_name] = inflated_node.serialized
            else:
                if not serialized.get(property_name):
                    serialized[property_name] = []
                serialized[property_name].append(inflated_node.serialized)

        # Neo4j won't return back relationships it doesn't know about, so just make them empty
        # so that the keys are always consistent
        for property_name in null_properties:
            prop = getattr(self, property_name)
            if isinstance(prop, One) or isinstance(prop, ZeroOrOne):
                serialized[property_name] = None
            else:
                serialized[property_name] = []

        return serialized

    @classmethod
    def find_or_none(cls, identifier):
        """
        Find the node using the supplied identifier.

        This method should be overridden if the node class accepts multiple types of identifiers.
        :param str identifier: the identifier to search the node by
        :return: the node or None
        :rtype: EstuaryStructuredNode or None
        """
        for _, prop_def in cls.__all_properties__:
            if isinstance(prop_def, UniqueIdProperty):
                return cls.nodes.get_or_none(**{prop_def.name: identifier})

        raise RuntimeError('{0} has no UniqueIdProperty'.format(cls.__label__))

    @staticmethod
    def conditional_connect(relationship, new_node):
        """
        Wrap the connect and replace methods for conditional relationship handling.

        :param neomodel.RelationshipManager relationship: a relationship to connect on
        :param neomodel.StructuredNode new_node: the node to create the relationship with
        :raises NotImplementedError: if this method is called with a relationship of cardinality of
            one
        """
        if new_node not in relationship:
            if len(relationship) == 0:
                relationship.connect(new_node)
            else:
                if isinstance(relationship, ZeroOrOne):
                    relationship.replace(new_node)
                elif isinstance(relationship, One):
                    raise NotImplementedError(
                        'conditional_connect doesn\'t support cardinality of one')
                else:
                    relationship.connect(new_node)

    @property
    def unique_id_property(self):
        """
        Get the name of the UniqueIdProperty for the node.

        :return: a string containing name of the unique ID property of a node
        :rtype: str
        """
        for _, prop_def in self.__all_properties__:
            if isinstance(prop_def, UniqueIdProperty):
                return prop_def.name

    @staticmethod
    def inflate_results(results):
        """
        Inflate the results.

        :param str results: results obtained from Neo4j
        :return: a list of dictionaries containing serialized results received from Neo4j
        :rtype: list
        """
        results_list = []
        for raw_result in results:
            nodes = []
            for node in raw_result:
                if node:
                    inflated_node = inflate_node(node)
                    nodes.append(inflated_node)
            results_list.append(nodes)

        return results_list

    def add_label(self, new_label):
        """
        Add a Neo4j label to an existing node.

        :param str new_label: the new label to add to the node
        """
        self.cypher('MATCH (a) WHERE id(a)={{self}} SET a :{0}'.format(new_label))

    def remove_label(self, label):
        """
        Remove a Neo4j label from an existing node.

        :param str label: the label to be removed from the node
        """
        self.cypher('MATCH (a) WHERE id(a)={{self}} REMOVE a :{0}'.format(label))
