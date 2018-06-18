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


def get_correlated_nodes_count(results):
    """
    Iterate through the results and yield correlated nodes.

    :param list results: contains inflated results from Neo4j
    :return: yield the results count (int) received from Neo4j
    :rtype: generator
    """
    if len(results) < 2:
        raise RuntimeError('This function can\'t be called with one or zero elements')
    for index in range(len(results)):
        # If it's the last node in the story, the siblings for it are determined
        # depending on the correlated node prior to it in the story
        if index == len(results) - 1:
            yield get_correlated_nodes(results[index].__label__, results[index - 1],
                                       last=True, count=True)
        else:
            yield get_correlated_nodes(results[index].__label__, results[index + 1], count=True)


def get_correlated_nodes(curr_node_label, next_node, last=False, count=False):
    """
    Query Neo4j and return the count of results.

    :param str curr_node_label: node label for which the siblings count is to be calculated
    :param EstuaryStructuredNode next_node: correlated node to curr_node in the story/path
    :kwarg bool last: determines if it's the last node in the story/path
    :kwarg bool last: determines if only count of sibling nodes should be returned
    or the nodes themselves
    :return: siblings count of curr_node | sibling nodes
    :rtype: int | EstuaryStructuredNode
    """
    # To avoid circular imports
    from estuary.models.koji import KojiBuild
    from estuary.models.distgit import DistGitCommit

    next_node_label = next_node.__label__
    if curr_node_label == DistGitCommit.__label__:
        # Always consider the next node as a KojiBuild because if it's
        # a ContainerKojiBuild after a DistGitCommit, it should be
        # treated as a normal KojiBuild in the story flow
        next_node_label = KojiBuild.__label__
    elif last and next_node_label == 'ContainerKojiBuild':
        # Always consider the next node as a KojiBuild because if it's
        # a ContainerKojiBuild and the story ended on an Advisory it should be
        # treated as a normal KojiBuild in the story flow
        next_node_label = KojiBuild.__label__
    item_story_flow = story_flow(next_node_label)
    relationship = item_story_flow['backward_relationship'][:-1]
    if last:
        relationship = item_story_flow['forward_relationship'][:-1]

    query = ('MATCH (next_node:{next_label})-[:{rel}]-(sibling:{curr_label})'
             'WHERE id(next_node)= {next_node_id}').format(
        next_label=next_node_label, rel=relationship, curr_label=curr_node_label,
        next_node_id=next_node.id)

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
            'forward_label': DistGitCommit.__label__,
            'backward_relationship': None,
            'backward_label': None
        }
    elif label == DistGitCommit.__label__:
        return {
            'uid_name': DistGitCommit.hash_.db_property or DistGitCommit.hash.name,
            'forward_relationship': '{0}<'.format(
                DistGitCommit.koji_builds.definition['relation_type']),
            'forward_label': KojiBuild.__label__,
            'backward_relationship': '{0}>'.format(
                DistGitCommit.resolved_bugs.definition['relation_type']),
            'backward_label': BugzillaBug.__label__
        }
    elif label == KojiBuild.__label__:
        return {
            'uid_name': KojiBuild.id_.db_property or KojiBuild.id.name,
            'forward_relationship': '{0}<'.format(KojiBuild.advisories.definition['relation_type']),
            'forward_label': Advisory.__label__,
            'backward_relationship': '{0}>'.format(KojiBuild.commit.definition['relation_type']),
            'backward_label': DistGitCommit.__label__
        }
    elif label == Advisory.__label__:
        return {
            'uid_name': Advisory.id_.db_property or Advisory.id.name,
            'forward_relationship': '{0}<'.format(
                Advisory.triggered_freshmaker_event.definition['relation_type']),
            'forward_label': FreshmakerEvent.__label__,
            'backward_relationship': '{0}>'.format(
                Advisory.attached_builds.definition['relation_type']),
            'backward_label': KojiBuild.__label__
        }
    elif label == FreshmakerEvent.__label__:
        return {
            'uid_name': FreshmakerEvent.id_.db_property or FreshmakerEvent.id.name,
            'forward_relationship': '{0}>'.format(
                FreshmakerEvent.triggered_container_builds.definition['relation_type']),
            'forward_label': ContainerKojiBuild.__label__,
            'backward_relationship': '{0}>'.format(FreshmakerEvent.triggered_by_advisory
                                                   .definition['relation_type']),
            'backward_label': Advisory.__label__
        }
    elif label == ContainerKojiBuild.__label__:
        return {
            'uid_name': ContainerKojiBuild.id_.db_property or ContainerKojiBuild.id.name,
            'forward_relationship': '{0}<'.format(
                ContainerKojiBuild.advisories.definition['relation_type']),
            'forward_label': ContainerAdvisory.__label__,
            'backward_relationship': '{0}<'.format(
                ContainerKojiBuild.triggered_by_freshmaker_event.definition['relation_type']),
            'backward_label': FreshmakerEvent.__label__
        }
    elif label == ContainerAdvisory.__label__:
        return {
            'uid_name': ContainerAdvisory.id_.db_property or ContainerAdvisory.id.name,
            'forward_relationship': None,
            'forward_label': None,
            'backward_relationship': '{0}>'.format(
                ContainerAdvisory.attached_builds.definition['relation_type']),
            'backward_label': ContainerKojiBuild.__label__
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
        data.append(serialized_node)
    return {
        'data': data,
        'meta': {
            'story_related_nodes': list(get_correlated_nodes_count(results)),
            'requested_node_index': requested_node_index
        }
    }
