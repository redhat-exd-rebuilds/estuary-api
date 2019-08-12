# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import abc
import sys

from neomodel import db
from datetime import datetime

from estuary.error import ValidationError
from estuary.models.koji import ContainerKojiBuild, KojiBuild, ModuleKojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory, ContainerAdvisory
from estuary.models.freshmaker import FreshmakerEvent
from estuary import log


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

    def get_wait_times(self, results):
        """
        Get the wait time between two artifacts for each pair of them, and the sum of these times.

        :param list results: contains inflated results from Neo4j
        :return: tuple with list of wait time ints in order of the story (oldest to newest), and
            a total wait time
        :rtype: tuple
        :raises RuntimeError: if results has less than 2 elements
        """
        len_story = len(results)
        if len_story < 2:
            return [0], 0

        # Some services do not have a real completion time because they perform a single action
        # that takes a negligible amount of time
        completion_times = {
            'BugzillaBug': 'creation_time',
            'DistGitCommit': 'commit_date',
            'Advisory': 'status_time',
            'ContainerAdvisory': 'status_time',
            # Although Freshmaker has a duration, we need to see how long it takes to trigger a
            # ContainerKojiBuild from when it started
            'FreshmakerEvent': 'time_created',
            'KojiBuild': 'completion_time',
            'ModuleKojiBuild': 'completion_time',
            'ContainerKojiBuild': 'completion_time'
        }

        total_wait_time = 0
        wait_times = [None for i in range(len_story - 1)]

        for index in range(len_story - 1):
            artifact = results[index]
            next_artifact = results[index + 1]
            property_name = completion_times[artifact.__label__]
            completion_time = getattr(artifact, property_name)
            if not completion_time or not next_artifact.timeline_datetime:
                continue

            if next_artifact.__label__.endswith('Advisory'):
                if next_artifact.attached_build_time(next_artifact, artifact):
                    next_artifact_start_time = next_artifact.attached_build_time(next_artifact,
                                                                                 artifact)
                else:
                    id_num = getattr(next_artifact, artifact.unique_id_property + '_')
                    log.warning(
                        'While calculating the wait time, a %s with ID %s was '
                        'encountered without an attached build time.',
                        next_artifact.__label__, id_num
                    )
                    continue
            else:
                next_artifact_start_time = next_artifact.timeline_datetime

            # Remove timezone info so that both are offset naive and thus able to be subtracted
            next_artifact_start_time = next_artifact_start_time.replace(tzinfo=None)
            completion_time = completion_time.replace(tzinfo=None)

            # Ensure that the artifacts are sequential
            if completion_time > next_artifact_start_time:
                continue

            # Find the time between when the current artifact completes and the next one starts
            wait_time = next_artifact_start_time - completion_time
            wait_times[index] = wait_time.total_seconds()

            # The 'wait time' between a FreshmakerEvent and a ContainerKojiBuild is still a part of
            # the processing in a FreshmakerEvent, so we do not count it towards the total wait time
            if artifact.__label__ != 'FreshmakerEvent':
                total_wait_time += wait_time.total_seconds()

        return wait_times, total_wait_time

    def get_total_processing_time(self, results):
        """
        Get the total time spent processing the story.

        :param list results: contains inflated results from Neo4j
        :return: the seconds of total time spent processing with a flag for inaccurate calculations
        :rtype: tuple
        """
        flag = False
        total = 0
        # If there is a build in the story, it will be assigned here so that it can later be
        # checked to see if it was attached to an advisory in the story
        build = None
        timed_processes = {
            'FreshmakerEvent': ['time_created', 'time_done'],
            'KojiBuild': ['creation_time', 'completion_time'],
            'ModuleKojiBuild': ['creation_time', 'completion_time'],
            'ContainerKojiBuild': ['creation_time', 'completion_time'],
            'Advisory': ['created_at', 'status_time'],
            'ContainerAdvisory': ['created_at', 'status_time']
        }
        for index, artifact in enumerate(results):
            if artifact.__label__ not in timed_processes:
                continue

            creation_time = getattr(artifact, timed_processes[artifact.__label__][0])
            if not creation_time:
                id_num = getattr(artifact, artifact.unique_id_property + '_')
                log.warning(
                    'While calculating the total processing time, a %s with ID %s was encountered '
                    'without a creation time.',
                    artifact.__label__, id_num
                )
                flag = True
                continue

            if artifact.__label__.endswith('KojiBuild'):
                build = artifact

            if artifact.__label__.endswith('Advisory'):
                if artifact.state in ['SHIPPED_LIVE', 'DROPPED_NO_SHIP']:
                    completion_time = getattr(artifact, timed_processes[artifact.__label__][1])
                else:
                    completion_time = datetime.utcnow()
                if build:
                    creation_time = artifact.attached_build_time(artifact, build)
                    if not creation_time:
                        creation_time = getattr(build, timed_processes[build.__label__][1])
                if not build or not creation_time:
                    log.warning(
                        'While calculating the processing time, a %s with ID %s was '
                        'encountered without a build or creation time.',
                        artifact.__label__, getattr(artifact,
                                                    artifact.unique_id_property + '_'))
                    continue

            # We do not want the processing time of the entire FreshmakerEvent, just the
            # processing time until the displayed ContainerKojiBuild is created
            elif artifact.__label__ == 'FreshmakerEvent':
                if index != len(results) - 1:
                    next_artifact = results[index + 1]
                    completion_time = getattr(next_artifact,
                                              timed_processes[next_artifact.__label__][0])
                elif artifact.state_name in ['COMPLETE', 'SKIPPED', 'FAILED', 'CANCELED']:
                    completion_time = getattr(artifact, timed_processes['FreshmakerEvent'][1])
                    if completion_time is None:
                        id_num = getattr(artifact, artifact.unique_id_property + '_')
                        log.warning(
                            'While calculating the total processing time, a %s with ID %s was '
                            'encountered without a completion time or subsequent build.',
                            artifact.__label__, id_num
                        )
                        flag = True
                        continue
                else:
                    completion_time = datetime.utcnow()

            else:
                completion_time = getattr(artifact, timed_processes[artifact.__label__][1])
                if not completion_time:
                    completion_time = datetime.utcnow()

            # Remove timezone info so that both are offset naive and thus able to be subtracted
            creation_time = creation_time.replace(tzinfo=None)
            completion_time = completion_time.replace(tzinfo=None)
            processing_time = completion_time - creation_time

            if processing_time.total_seconds() < 0:
                id_num = getattr(artifact, artifact.unique_id_property + '_')
                log.warning(
                    'A negative processing time was calculated, with a %s with ID %s.',
                    artifact.__label__, id_num
                )
            else:
                total += processing_time.total_seconds()

        return total, flag

    def get_total_lead_time(self, results):
        """
        Get the total lead time - the time from the start of a story until its current state.

        :param list results: contains inflated results from Neo4j
        :return: the seconds of total time in the story, or None if sufficient data is not available
        :rtype: int or None
        """
        first_artifact = results[0]
        last_artifact = results[-1]
        times = {
            'BugzillaBug': ['creation_time', None],
            'DistGitCommit': ['commit_date', None],
            'Advisory': ['created_at', None],
            'ContainerAdvisory': ['created_at', None],
            'FreshmakerEvent': ['time_created', 'time_done'],
            'KojiBuild': ['creation_time', 'completion_time'],
            'ModuleKojiBuild': ['creation_time', 'completion_time'],
            'ContainerKojiBuild': ['creation_time', 'completion_time']
        }

        start_time_key = times[first_artifact.__label__][0]
        start_time = getattr(first_artifact, start_time_key)
        if not start_time:
            id_num = getattr(first_artifact, first_artifact.unique_id_property + '_')
            log.warning(
                'While calculating the total lead time, a %s with ID %s was encountered '
                'without a creation time.',
                first_artifact.__label__, id_num
            )
            return
        end_time_key = times[last_artifact.__label__][1]

        if end_time_key:
            end_time = getattr(last_artifact, end_time_key)
            if not end_time:
                end_time = datetime.utcnow()
        elif last_artifact.__label__.endswith('Advisory'):
            if last_artifact.state in ['SHIPPED_LIVE', 'DROPPED_NO_SHIP']:
                end_time = getattr(last_artifact, 'status_time')
            else:
                end_time = datetime.utcnow()
        else:
            end_time = getattr(last_artifact, start_time_key)

        # Remove timezone info so that both are offset naive and thus able to be subtracted
        start_time = start_time.replace(tzinfo=None)
        end_time = end_time.replace(tzinfo=None)
        total = end_time - start_time
        if total.total_seconds() < 0:
            first_id_num = getattr(first_artifact, first_artifact.unique_id_property + '_')
            last_id_num = getattr(last_artifact, last_artifact.unique_id_property + '_')
            log.warning(
                'A negative total lead time was calculated, in a story starting with a %s with ID '
                '%s and ending with a %s with ID %s.',
                first_artifact.__label__, first_id_num, last_artifact.__label__, last_id_num
            )
            return 0
        return total.total_seconds()

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
            serialized_node['timeline_timestamp'] = node.timeline_timestamp
            data.append(serialized_node)

        base_instance = BaseStoryManager()
        wait_times, total_wait_time = base_instance.get_wait_times(results)
        total_processing_time = 0
        processing_time_flag = False
        total_lead_time = 0
        try:
            processing_time, flag = base_instance.get_total_processing_time(results)
            total_processing_time = processing_time
            processing_time_flag = flag
        except:  # noqa E722
            log.exception('Failed to compute total processing time statistic.')
        try:
            total_lead_time = base_instance.get_total_lead_time(results)
        except:  # noqa E722
            log.exception('Failed to compute total lead time statistic.')
        formatted_results = {
            'data': data,
            'meta': {
                'story_related_nodes_forward': list(self.get_sibling_nodes_count(results)),
                'story_related_nodes_backward': list(
                    self.get_sibling_nodes_count(results, reverse=True)),
                'requested_node_index': requested_node_index,
                'story_type': self.__class__.__name__[:-12].lower(),
                'wait_times': wait_times,
                'total_wait_time': total_wait_time,
                'total_processing_time': total_processing_time,
                'processing_time_flag': processing_time_flag,
                'total_lead_time': total_lead_time
            }
        }
        return formatted_results

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
