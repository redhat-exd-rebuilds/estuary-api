# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from datetime import datetime

from six import text_type
from neomodel import db

from estuary import log
from estuary.error import ValidationError


def timestamp_to_datetime(timestamp):
    """
    Convert a string timestamp to a datetime object.

    :param str timestamp: a generic or ISO-8601 timestamp
    :return: datetime object of the timestamp
    :rtype: datetime.datetime
    :raises ValueError: if the timestamp is an unsupported or invalid format
    """
    log.debug('Trying to parse the timestamp "{0}"'.format(timestamp))
    error_msg = 'The timestamp "{0}" is an invalid format'.format(timestamp)
    combinations = (
        (r'^(?P<datetime>\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})(?:\.\d+)?$',
         '%Y-%m-%d %H:%M:%S'),
        (r'^(?P<datetime>\d{4}-\d{1,2}-\d{1,2})$', '%Y-%m-%d'),
        # ISO 8601 format
        (r'^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:Z|[-+]00(?::00)?)?$',
         '%Y-%m-%dT%H:%M:%S'))

    for combination in combinations:
        regex_match = re.match(combination[0], timestamp)
        if regex_match:
            try:
                return datetime.strptime(regex_match.group('datetime'), combination[1])
            except ValueError:
                # In case the user asked for an unreleastic date like "2020:99:99"
                raise ValueError(error_msg)

    raise ValueError(error_msg)


def timestamp_to_date(timestamp):
    """
    Convert a string timestamp to a date object.

    :param str timestamp: a generic or ISO-8601 timestamp
    :return: date object of the timestamp
    :rtype: datetime.date
    :raises ValueError: if the timestamp is an unsupported or invalid format
    """
    return timestamp_to_datetime(timestamp).date()


def str_to_bool(item):
    """
    Convert a string to a boolean.

    :param str item: string to parse
    :return: a boolean equivalent
    :rtype: boolean
    """
    if isinstance(item, text_type):
        return item.lower() in ('true', '1')
    else:
        return False


def inflate_node(result):
    """
    Inflate a Neo4j result to a neomodel model object.

    :param neo4j.v1.types.Node result: a node from a cypher query result
    :return: a model (EstuaryStructuredNode) object
    """
    # To prevent a ciruclar import, this must be imported here
    from estuary.models import names_to_model

    if 'ContainerKojiBuild' in result.labels:
        result_label = 'ContainerKojiBuild'
    elif 'ContainerAdvisory' in result.labels:
        result_label = 'ContainerAdvisory'
    elif len(result.labels) > 1:
        raise RuntimeError('inflate_node encounted a node with multiple labels: {0}. '
                           'Which one should be used?'.format(', '.join(result.labels)))
    else:
        result_label = list(result.labels)[0]

    if result_label in names_to_model:
        node_model = names_to_model[result_label]
    else:
        # This should never happen unless Neo4j returns labels that aren't associated with
        # classes in all_models
        raise RuntimeError('A StructuredNode couldn\'t be found from the labels: {0}'.format(
            ', '.join(result.labels)))

    return node_model.inflate(result)


def get_neo4j_node(resource_name, uid):
    """
    Get a Neo4j node based on a label and unique identifier.

    :param str resource_name: a neomodel model label
    :param str uid: a string of the unique identifier defined in the neomodel model
    :return: a neomodel model object
    :raises ValidationError: if the requested resource doesn't exist or doesn't have a
    UniqueIdProperty
    """
    # To prevent a ciruclar import, we must import this here
    from estuary.models import all_models

    for model in all_models:
        if model.__label__.lower() == resource_name.lower():
            try:
                return model.find_or_none(uid)
            except RuntimeError:
                # There is no UniqueIdProperty on this model so raise an exception
                models_wo_uid = ('DistGitRepo', 'DistGitBranch')
                model_names = [model.__name__.lower() for model in all_models
                               if model.__name__ not in models_wo_uid]
                error = ('The requested resource "{0}" is invalid. Choose from the following: '
                         '{1}, and {2}.'.format(resource_name, ', '.join(model_names[:-1]),
                                                model_names[-1]))
                raise ValidationError(error)


def create_story_query(item, node_id, reverse=False, limit=False):
    """
    Create a raw cypher query for story of an artifact.

    :param node item: a Neo4j node whose story is requested by the user
    :param int node_id: the internal Neo4j ID of the node
    :param bool reverse: boolean value to specify the direction to proceed
    from current node corresponding to the story_flow
    :return: a string containing raw cypher query to retrieve the story of an artifact from Neo4j
    :rtype: str
    """
    # To avoid circular imports
    from estuary.models import story_flow_list

    query = ''

    if reverse is True:
        rel_label = 'backward_relationship'
        node_label = 'backward_label'
    else:
        rel_label = 'forward_relationship'
        node_label = 'forward_label'

    curr_node_label = item.__label__
    if curr_node_label not in story_flow_list:
        raise ValidationError('The story is not available for this kind of resource')

    while True:
        curr_node_info = story_flow(curr_node_label)
        if not curr_node_info:
            break

        if curr_node_label == item.__label__:
            query = """\
                MATCH ({var}:{label}) WHERE id({var})= {node_id}
                CALL apoc.path.expandConfig({var}, {{sequence:\'{label}
                """.format(var=curr_node_label.lower(), label=curr_node_label, node_id=node_id)

        query += ', {0}, {1}'.format(curr_node_info[rel_label], curr_node_info[node_label])

        curr_node_label = curr_node_info[node_label]

    if query:
        query += """\
            \', minLevel:1}) YIELD path
            RETURN path
            ORDER BY length(path) DESC
            """

    if query and limit:
        query += ' LIMIT 1'

    return query


def get_sibling_nodes_count(results, reverse=False):
    """
    Iterate through the results and yield correlated nodes.

    :param list results: contains inflated results from Neo4j
    :kwarg bool reverse: determines the direction the story is traversed in (i.e. forward/backward)
    :return: yield the results count (int) received from Neo4j
    :rtype: generator
    """
    len_story = len(results)
    if len_story < 2:
        raise RuntimeError('This function can\'t be called with one or zero elements')

    correlated_nodes = []
    if not reverse:
        for index in range(len_story - 1):
            correlated_nodes.append(get_sibling_nodes(
                results[index].__label__, results[index + 1], count=True))
    else:
        # Iterate over results backwards for convenience -- will be reversed to correct order later
        for index in range(len_story - 1, 0, -1):
            correlated_nodes.append(get_sibling_nodes(
                results[index].__label__, results[index - 1], count=True))

    # When traversing the story, the last node is skipped because there is no next node for it, so
    # we must add a value of 0 as a placeholder
    correlated_nodes.append(0)
    if reverse:
        return correlated_nodes[::-1]
    return correlated_nodes


def get_sibling_nodes(siblings_node_label, story_node, count=False):
    """
    Return sibling nodes with the label siblings_node_label that are related to story_node.

    :param str siblings_node_label: node label for which the siblings count is to be calculated
    :param EstuaryStructuredNode story_node: node in the story that has the desired relationships
    with the siblings (specified with siblings_node_label)
    :kwarg bool count: determines if only count of sibling nodes should be returned
    or the nodes themselves
    :return: siblings count of curr_node | sibling nodes
    :rtype: int | EstuaryStructuredNode
    """
    item_story_flow = story_flow(story_node.__label__)
    # Based on the desired siblings label, we can determine which story_node relationship to query
    # for
    if item_story_flow['forward_label'] == siblings_node_label:
        relationship = item_story_flow['forward_relationship'][:-1]
    elif item_story_flow['backward_label'] == siblings_node_label:
        relationship = item_story_flow['backward_relationship'][:-1]
    else:
        RuntimeError('The node with label "{0}" does not have a relationship with nodes of label '
                     '"{1}"'.format(story_node.__label__, siblings_node_label))

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
        # We reduce the count by one to not account for the node already being shown in the story
        return count - 1
    else:
        query += ' RETURN sibling'
        results, _ = db.cypher_query(query)
        return results


def story_flow(label):
    """
    Get the next/previous node in a story flow/pipeline path.

    :param str label: Neo4j node label
    :return: uid and relationship information in both forward and backward directions
    :rtype: dict
    """
    # To avoid circular imports
    from estuary.models.koji import ContainerKojiBuild, KojiBuild
    from estuary.models.bugzilla import BugzillaBug
    from estuary.models.distgit import DistGitCommit
    from estuary.models.errata import Advisory, ContainerAdvisory
    from estuary.models.freshmaker import FreshmakerEvent

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
            'forward_relationship': '{0}<'.format(KojiBuild.advisories.definition['relation_type']),
            'forward_relationship_display': 'that contain',
            'forward_label': Advisory.__label__,
            'forward_label_display': 'advisory',
            'backward_relationship': '{0}>'.format(KojiBuild.commit.definition['relation_type']),
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
                FreshmakerEvent.triggered_container_builds.definition['relation_type']),
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


def format_story_results(results, requested_item):
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
            'story_related_nodes_forward': list(get_sibling_nodes_count(results)),
            'story_related_nodes_backward': list(
                get_sibling_nodes_count(results, reverse=True)),
            'requested_node_index': requested_node_index
        }
    }


def set_story_labels(requested_node_label, results, reverse=False):
    """
    Replace Neo4j labels with appropriate labels of the story flow.

    :param string requested_node_label: label of the node requested by the user
    :param list results: nodes in a story/path
    :kwarg bool reverse: determines if the results are in reverse order of the story flow
    :return: results with story/path labels
    :rtype: list
    """
    # Avoid circular imports
    from estuary.models import story_flow_list

    if not results:
        return results

    idx = 0
    if reverse:
        idx = len(results) - 1
    delta = -1 if reverse else 1
    node_idx = story_flow_list.index(requested_node_label)
    while (0 <= idx < len(results)):
        results[idx].__label__ = story_flow_list[node_idx]
        idx += delta
        node_idx += delta
    return results


def get_siblings_description(story_node_display_name, story_node_story_flow, backward):
    """
    Generate a description of the siblings.

    :param string story_node_display_name: the preformatted name to be displayed for the story node
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
        raise RuntimeError('A node with the label {0} does not have a {1} relationship'.format(
            story_node_story_flow['display_label'], rel_direction))
