# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from datetime import datetime
from six import text_type

from neomodel import UniqueIdProperty, db

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
            for _, prop_def in model.__all_properties__:
                if isinstance(prop_def, UniqueIdProperty):
                    return model.nodes.get_or_none(**{prop_def.name: uid})

    # Some models don't have unique ID's and those should be skipped
    models_wo_uid = ('DistGitRepo', 'DistGitBranch')
    model_names = [model.__name__.lower() for model in all_models
                   if model.__name__ not in models_wo_uid]
    error = ('The requested resource "{0}" is invalid. Choose from the following: '
             '{1}, and {2}.'.format(resource_name, ', '.join(model_names[:-1]), model_names[-1]))
    raise ValidationError(error)


def create_node_subquery(node_label, uid_name=None, uid=None):
    """
    Build part of a raw cypher query for a node label.

    :param str node_label: a Neo4j node label
    :kwarg str uid_name: name of node's UniqueIdProperty
    :kwarg str uid: value of node's UniqueIdProperty
    :return: the node represented in raw cypher
    :rtype: str
    """
    if uid_name and uid:
        return '({0}:{1} {{{2}:"{3}"}})'.format(node_label.lower(), node_label,
                                                uid_name.rstrip('_'), uid)
    return '({0}:{1})'.format(node_label.lower(), node_label)


def create_story_query(item, uid_name, uid, reverse=False, limit=False):
    """
    Create a raw cypher query for story of an artifact.

    :param node item: a Neo4j node whose story is requested by the user
    :param str uid_name: name of node's UniqueIdProperty
    :param str uid: value of node's UniqueIdProperty
    :param bool reverse: boolean value to specify the direction to proceed
    from current node corresponding to the story_flow
    :return: a string containing raw cypher query to retrieve the story of an artifact from Neo4j
    :rtype: str
    """
    # To avoid circular imports
    from purview.models import story_flow_list

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
                MATCH ({var}:{label} {{{uid_name}:"{uid}"}})
                CALL apoc.path.expandConfig({var}, {{sequence:\'{label}
                """.format(var=curr_node_label.lower(),
                           label=curr_node_label,
                           uid_name=uid_name.rstrip('_'),
                           uid=uid)

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


def get_corelated_nodes(results):
    """
    Create a raw cypher query for story nodes and get a count of the nodes co-related to them.

    :param dict results: a dictionary containing story nodes
    :return: a dictionary containing counts of all co-related nodes from Neo4j
    :rtype: dict
    """
    # To avoid circular imports
    from purview.models.bugzilla import BugzillaBug

    nodes_count_dict = {}
    curr_label = BugzillaBug.__label__
    last = False
    while not last:
        node_count = 0
        next_node_info = story_flow(curr_label)
        forward_label = next_node_info['forward_label']
        if forward_label in results:
            query = 'MATCH '
            # Only grab the first element since there will only be one
            next_node = results[forward_label][0]
            forward_rel = next_node_info['forward_relationship'][:-1]
            uid_name = story_flow(forward_label)['uid_name']
            node_subquery = create_node_subquery(curr_label)
            next_node_subquery = create_node_subquery(forward_label, uid_name, next_node[uid_name])
            query += '{0}-[:{1}]-{2}\n'.format(node_subquery, forward_rel, next_node_subquery)
            query += 'RETURN COUNT({0}) AS count'.format(curr_label.lower())
            node_count = get_node_count(query)

        backward_label = next_node_info['backward_label']
        # If this evaluates to true, then this is the end of the story for the node, so we get
        # the backwards related nodes (e.g. all the ContainerBuild that were triggered by a
        # Freshmaker event)
        if (not forward_label or forward_label not in results) and backward_label:
            last = True
            if backward_label not in results:
                continue
            query = 'MATCH '
            backward_node = results[backward_label][0]
            backward_rel = next_node_info['backward_relationship'][:-1]
            uid_name = story_flow(backward_label)['uid_name']
            node_subquery = create_node_subquery(backward_label, uid_name, backward_node[uid_name])
            next_node_subquery = create_node_subquery(curr_label)
            query += '{0}-[:{1}]-{2}\n'.format(node_subquery, backward_rel, next_node_subquery)
            query += 'RETURN COUNT({0}) AS count'.format(curr_label.lower())
            node_count = get_node_count(query)

        # If there are related nodes, then there always be at least a value of one because it
        # includes the node already in the story. This is why we subtract here.
        if node_count > 0:
            nodes_count_dict[curr_label] = node_count - 1

        curr_label = forward_label

    return nodes_count_dict


def get_node_count(query):
    """
    Query Neo4j and return the count of results.

    :param str query: raw cypher query
    :return: a dictionary containing the results count received from Neo4j.
    :rtype: int
    """
    results_dict = {}
    results, _ = db.cypher_query(query)

    if not results:
        return results_dict

    return results[0][0]


def _order_story_results(result):
    """
    Order results to follow the story flow sequence.

    :param dict results: contains serialized results from Neo4j
    :return: a dict containing results ordered in the story flow sequence
    :rtype: dict
    """
    results = {'data': [], 'meta': {'related_nodes': {}}}
    curr_label = 'BugzillaBug'
    while curr_label:
        results['meta']['related_nodes'][curr_label] = 0
        if curr_label in result:
            results['data'].append(result[curr_label][0])

        curr_label = story_flow(curr_label)['forward_label']

    results['meta']['related_nodes'].update(get_corelated_nodes(result))

    return results


def story_flow(label):
    """
    Get the next/previous node in a story flow/pipeline path.

    :param str label: Neo4j node label
    :return: uid and relationship information in both forward and backward directions
    :rtype: dict
    """
    # To avoid circular imports
    from purview.models.koji import ContainerKojiBuild, KojiBuild
    from purview.models.bugzilla import BugzillaBug
    from purview.models.distgit import DistGitCommit
    from purview.models.errata import Advisory
    from purview.models.freshmaker import FreshmakerEvent

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
            'uid_name': KojiBuild.id_.db_property or KojiBuild.id.name,
            'forward_relationship': None,
            'forward_label': None,
            'backward_relationship': '{0}<'.format(
                ContainerKojiBuild.triggered_by_freshmaker_event.definition['relation_type']),
            'backward_label': FreshmakerEvent.__label__
        }
    else:
        raise ValueError('The label should belong to a Neo4j node class')
