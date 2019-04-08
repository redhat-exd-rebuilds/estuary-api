# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import abc
import sys

from neomodel import db

from estuary.error import ValidationError
from estuary.models.koji import ContainerKojiBuild, KojiBuild, ModuleKojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory, ContainerAdvisory
from estuary.models.freshmaker import FreshmakerEvent


class BaseStoryManager(object):
    """A class containing utility methods to create a story for an artifact."""

    @staticmethod
    def get_story_manager(item, config, limit=False):
        """
        Select which story flow to follow.

        :param node item: a Neo4j node whose story is requested by the user
        :param flask.config.Config config: flask config
        :kwarg bool limit: specifies if LIMIT keyword should be added to the created cypher query
        :return: instance of one of the story manager classes
        :rtype: ModuleStoryManager/ContainerStoryManager
        """
        for class_name in config['STORY_MANAGER_SEQUENCE']:
            story_manager_cls = getattr(sys.modules[__name__], class_name, None)
            if not story_manager_cls:
                raise RuntimeError('Story manager class of {0} could not be found'
                                   .format(class_name))
            story_manager = story_manager_cls()
            story_manager.forward_story = story_manager.get_story_nodes(item, limit=limit)
            story_manager.backward_story = story_manager.get_story_nodes(
                item, reverse=True, limit=limit)

            if story_manager.is_valid():
                return story_manager

        return story_manager

    def get_story_nodes(self, item, reverse=False, limit=False):
        """
        Create a raw cypher query for story of an artifact and query neo4j with it.

        :param node item: a Neo4j node whose story is requested by the user
        :kwarg bool reverse: specifies the direction to proceed from current node
            corresponding to the story_flow
        :kwarg bool limit: specifies if LIMIT keyword should be added to the created cypher query
        :return: story paths for a particular artifact
        :rtype: list
        """
        query = ''

        if reverse is True:
            rel_label = 'backward_relationship'
            node_label = 'backward_label'
        else:
            rel_label = 'forward_relationship'
            node_label = 'forward_label'

        curr_node_label = item.__label__
        if curr_node_label not in self.story_flow_list:
            raise ValidationError('The story is not available for this kind of resource')

        while True:
            curr_node_info = self.story_flow(curr_node_label)
            if not curr_node_info:
                break

            if curr_node_label == item.__label__:
                query = """\
                    MATCH ({var}:{label}) WHERE id({var})= {node_id}
                    CALL apoc.path.expandConfig({var}, {{sequence:\'{label}
                    """.format(
                        var=curr_node_label.lower(), label=curr_node_label, node_id=item.id)

            query += ', {0}, {1}'.format(curr_node_info[rel_label],
                                         curr_node_info[node_label])

            curr_node_label = curr_node_info[node_label]

        if query:
            query += """\
                \', minLevel:1}) YIELD path
                RETURN path
                ORDER BY length(path) DESC
                """

        if query and limit:
            query += ' LIMIT 1'

        results = []
        if query:
            results, _ = db.cypher_query(query)
        return results

    @abc.abstractmethod
    def story_flow(self, label):
        """
        Get the next/previous node in a story flow/pipeline path.

        :param str label: Neo4j node label
        :return: uid and relationship information in both forward and backward directions
        :rtype: dict
        """
        pass

    def get_sibling_nodes_count(self, results, reverse=False):
        """
        Iterate through the results and yield correlated nodes.

        :param list results: contains inflated results from Neo4j
        :kwarg bool reverse: determines the direction the story is traversed in
            (i.e. forward/backward)
        :return: yield the results count (int) received from Neo4j
        :rtype: generator
        """
        len_story = len(results)
        if len_story < 2:
            raise RuntimeError('This function can\'t be called with one or zero elements')

        correlated_nodes = []
        if not reverse:
            for index in range(len_story - 1):
                correlated_nodes.append(self.get_sibling_nodes(
                    results[index].__label__, results[index + 1], count=True))
        else:
            # Iterate over results backwards for convenience --
            # will be reversed to correct order later
            for index in range(len_story - 1, 0, -1):
                correlated_nodes.append(self.get_sibling_nodes(
                    results[index].__label__, results[index - 1], count=True))

        # When traversing the story, the last node is skipped because there is no next node for it,
        # so we must add a value of 0 as a placeholder
        correlated_nodes.append(0)
        if reverse:
            return correlated_nodes[::-1]
        return correlated_nodes

    def get_sibling_nodes(self, siblings_node_label, story_node, count=False):
        """
        Return sibling nodes with the label siblings_node_label that are related to story_node.

        :param str siblings_node_label: node label for which the siblings count is to be calculated
        :param EstuaryStructuredNode story_node: node in the story that has the desired
            relationships with the siblings (specified with siblings_node_label)
        :kwarg bool count: determines if only count of sibling nodes should be returned
            or the nodes themselves
        :return: siblings count of curr_node | sibling nodes
        :rtype: int | EstuaryStructuredNode
        """
        item_story_flow = self.story_flow(story_node.__label__)
        # Based on the desired siblings label, we can determine which story_node
        # relationship to query for
        if item_story_flow['forward_label'] == siblings_node_label:
            relationship = item_story_flow['forward_relationship'][:-1]
        elif item_story_flow['backward_label'] == siblings_node_label:
            relationship = item_story_flow['backward_relationship'][:-1]
        else:
            RuntimeError('The node with label "{0}" does not have a relationship with '
                         'nodes of label "{1}"'.format(story_node.__label__, siblings_node_label))

        query = ('MATCH (next_node:{next_label})-[:{rel}]-(sibling:{curr_label})'
                 'WHERE id(next_node)= {next_node_id}').format(
            next_label=story_node.__label__, rel=relationship, curr_label=siblings_node_label,
            next_node_id=story_node.id)

        if count:
            query += ' RETURN COUNT(sibling) as count'
            results, _ = db.cypher_query(query)
            count = results[0][0]
            if count == 0:
                return count
            # We reduce the count by one to ignore the node already being shown in the story
            return count - 1
        else:
            query += ' RETURN sibling'
            results, _ = db.cypher_query(query)
            return results

    def format_story_results(self, results, requested_item):
        """
        Format story results from Neo4j to the API format.

        :param list results: nodes in a story/path
        :param EstuaryStructuredNode requested_item: item requested by the user
        :return: results in API format
        :rtype: dict
        """
        data = []
        for i, node in enumerate(results):
            if node.id == requested_item.id:
                requested_node_index = i
                serialized_node = node.serialized_all
            else:
                serialized_node = node.serialized
            serialized_node['resource_type'] = node.__label__
            serialized_node['display_name'] = node.display_name
            data.append(serialized_node)
        return {
            'data': data,
            'meta': {
                'story_related_nodes_forward': list(self.get_sibling_nodes_count(results)),
                'story_related_nodes_backward': list(
                    self.get_sibling_nodes_count(results, reverse=True)),
                'requested_node_index': requested_node_index,
                'story_type': self.__class__.__name__[:-12].lower()
            }
        }

    def set_story_labels(self, requested_node_label, results, reverse=False):
        """
        Replace Neo4j labels with appropriate labels of the story flow.

        :param string requested_node_label: label of the node requested by the user
        :param list results: nodes in a story/path
        :kwarg bool reverse: determines if the results are in reverse order of the story flow
        :return: results with story/path labels
        :rtype: list
        """
        if not results:
            return results

        idx = 0
        if reverse:
            idx = len(results) - 1
        delta = -1 if reverse else 1
        node_idx = self.story_flow_list.index(requested_node_label)
        while (0 <= idx < len(results)):
            results[idx].__label__ = self.story_flow_list[node_idx]
            idx += delta
            node_idx += delta
        return results

    @staticmethod
    def get_siblings_description(story_node_display_name, story_node_story_flow, backward):
        """
        Generate a description of the siblings.

        :param string story_node_display_name: the preformatted name to be displayed for the story
            node
        :param dict story_node_story_flow: has forward and backward relationships of the story node
        :param bool backward: determines the relationship direction the story node has with the
            siblings in the story
        :return: returns the appropriate siblings title
        :rtype: string
        """
        def _get_plural_label(label):
            if label.endswith('y'):
                label = label[:-1] + 'ies'
            else:
                label = label + 's'
            return label

        if backward:
            rel_direction = 'backward'
        else:
            rel_direction = 'forward'

        rel_label = story_node_story_flow['{0}_label_display'.format(rel_direction)]

        if rel_label:
            rel_label = _get_plural_label(rel_label)
            relationship = \
                story_node_story_flow['{0}_relationship_display'.format(rel_direction)]
            result = '{0} {1} {2}'.format(rel_label, relationship, story_node_display_name)
            return result[0].upper() + result[1:]
        else:
            raise RuntimeError('{0} does not have a {1} relationship'.format(
                story_node_display_name, rel_direction))


class ContainerStoryManager(BaseStoryManager):
    """A class containing utility methods to create a container story."""

    def __init__(self):
        """Instantiate variables required to get container story of a node."""
        self.story_flow_list = ['BugzillaBug', 'DistGitCommit', 'KojiBuild',
                                'Advisory', 'FreshmakerEvent', 'ContainerKojiBuild',
                                'ContainerAdvisory']

    def story_flow(self, label):
        """
        Get the next/previous node in a story flow/pipeline path.

        :param str label: Neo4j node label
        :return: uid and relationship information in both forward and backward directions
        :rtype: dict
        """
        if not label:
            return

        if label == BugzillaBug.__label__:
            return {
                'uid_name': BugzillaBug.id_.db_property or BugzillaBug.id.name,
                'forward_relationship': '{0}<'.format(
                    BugzillaBug.resolved_by_commits.definition['relation_type']),
                'forward_relationship_display': 'that resolved',
                'forward_label': DistGitCommit.__label__,
                'forward_label_display': 'commit',
                'backward_relationship': None,
                'backward_relationship_display': None,
                'backward_label': None,
                'backward_label_display': None
            }
        elif label == DistGitCommit.__label__:
            return {
                'uid_name': DistGitCommit.hash_.db_property or DistGitCommit.hash.name,
                'forward_relationship': '{0}<'.format(
                    DistGitCommit.koji_builds.definition['relation_type']),
                'forward_relationship_display': 'built by',
                'forward_label': KojiBuild.__label__,
                'forward_label_display': 'build',
                'backward_relationship': '{0}>'.format(
                    DistGitCommit.resolved_bugs.definition['relation_type']),
                'backward_relationship_display': 'resolved by',
                'backward_label': BugzillaBug.__label__,
                'backward_label_display': 'Bugzilla bug'
            }
        elif label == KojiBuild.__label__:
            return {
                'uid_name': KojiBuild.id_.db_property or KojiBuild.id.name,
                'forward_relationship': '{0}<'.format(
                    KojiBuild.advisories.definition['relation_type']),
                'forward_relationship_display': 'that contain',
                'forward_label': Advisory.__label__,
                'forward_label_display': 'advisory',
                'backward_relationship': '{0}>'.format(
                    KojiBuild.commit.definition['relation_type']),
                'backward_relationship_display': 'that built',
                'backward_label': DistGitCommit.__label__,
                'backward_label_display': 'commit'
            }
        elif label == Advisory.__label__:
            return {
                'uid_name': Advisory.id_.db_property or Advisory.id.name,
                'forward_relationship': '{0}<'.format(
                    Advisory.triggered_freshmaker_event.definition['relation_type']),
                'forward_relationship_display': 'triggered by',
                'forward_label': FreshmakerEvent.__label__,
                'forward_label_display': 'Freshmaker event',
                'backward_relationship': '{0}>'.format(
                    Advisory.attached_builds.definition['relation_type']),
                'backward_relationship_display': 'attached to',
                'backward_label': KojiBuild.__label__,
                'backward_label_display': 'build'
            }
        elif label == FreshmakerEvent.__label__:
            return {
                'uid_name': FreshmakerEvent.id_.db_property or FreshmakerEvent.id.name,
                'forward_relationship': '{0}>'.format(
                    FreshmakerEvent.successful_koji_builds.definition['relation_type']),
                'forward_relationship_display': 'triggered by',
                'forward_label': ContainerKojiBuild.__label__,
                'forward_label_display': 'container build',
                'backward_relationship': '{0}>'.format(FreshmakerEvent.triggered_by_advisory
                                                       .definition['relation_type']),
                'backward_relationship_display': 'that triggered',
                'backward_label': Advisory.__label__,
                'backward_label_display': 'advisory'
            }
        elif label == ContainerKojiBuild.__label__:
            return {
                'uid_name': ContainerKojiBuild.id_.db_property or ContainerKojiBuild.id.name,
                'forward_relationship': '{0}<'.format(
                    ContainerKojiBuild.advisories.definition['relation_type']),
                'forward_relationship_display': 'that contain',
                'forward_label': ContainerAdvisory.__label__,
                'forward_label_display': 'container advisory',
                'backward_relationship': '{0}<'.format(
                    ContainerKojiBuild.triggered_by_freshmaker_event.definition['relation_type']),
                'backward_relationship_display': 'that triggered',
                'backward_label': FreshmakerEvent.__label__,
                'backward_label_display': 'Freshmaker event'
            }
        elif label == ContainerAdvisory.__label__:
            return {
                'uid_name': ContainerAdvisory.id_.db_property or ContainerAdvisory.id.name,
                'forward_relationship': None,
                'forward_relationship_display': None,
                'forward_label': None,
                'forward_label_display': None,
                'backward_relationship': '{0}>'.format(
                    ContainerAdvisory.attached_builds.definition['relation_type']),
                'backward_relationship_display': 'attached to',
                'backward_label': ContainerKojiBuild.__label__,
                'backward_label_display': 'container build'
            }
        else:
            raise ValueError('The label should belong to a Neo4j node class')

    def is_valid(self):
        """
        Determine if the story path matches the returned story.

        :return: whether story is valid for this story path
        :rtype: bool
        """
        # This is the default story flow if no other story flow works out
        return True


class ModuleStoryManager(ContainerStoryManager):
    """A class containing utility methods to create a module story."""

    def __init__(self):
        """Instantiate variables required to get module story of a node."""
        self.story_flow_list = ['BugzillaBug', 'DistGitCommit', 'KojiBuild',
                                'ModuleKojiBuild', 'Advisory', 'FreshmakerEvent',
                                'ContainerKojiBuild', 'ContainerAdvisory']

    def story_flow(self, label):
        """
        Get the next/previous node in a story flow/pipeline path.

        :param str label: Neo4j node label
        :return: uid and relationship information in both forward and backward directions
        :rtype: dict
        """
        if label == ModuleKojiBuild.__label__:
            return {
                'uid_name': ModuleKojiBuild.id_.db_property or ModuleKojiBuild.id.name,
                'forward_relationship': '{0}<'.format(
                    KojiBuild.advisories.definition['relation_type']),
                'forward_relationship_display': 'that contain',
                'forward_label': Advisory.__label__,
                'forward_label_display': 'advisory',
                'backward_relationship': '{0}>'.format(
                    ModuleKojiBuild.components.definition['relation_type']),
                'backward_relationship_display': 'that contain',
                'backward_label': KojiBuild.__label__,
                'backward_label_display': 'build'
            }

        flow_dict = super(ModuleStoryManager, self).story_flow(label)

        if label == KojiBuild.__label__:
            flow_dict.update({
                'forward_relationship': '{0}<'.format(
                    KojiBuild.module_builds.definition['relation_type']),
                'forward_relationship_display': 'attached to',
                'forward_label': ModuleKojiBuild.__label__,
                'forward_label_display': 'module build'
            })
        elif label == Advisory.__label__:
            flow_dict.update({
                'backward_label': ModuleKojiBuild.__label__,
                'backward_label_display': 'module build'
            })
        return flow_dict

    def is_valid(self):
        """
        Determine if the story path matches the returned story.

        :return: whether story is valid for this story path
        :rtype: bool
        """
        story = self.backward_story + self.forward_story
        story_nodes = [node[0].nodes for node in story]
        for path in story_nodes:
            for model in path:
                if model.labels.__contains__(ModuleKojiBuild.__label__):
                    return True

        return False
