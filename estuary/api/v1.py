# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import NotFound
from neomodel import db

from estuary import version
from estuary.models import story_flow_list
from estuary.models.base import EstuaryStructuredNode

from estuary.utils.general import (
    str_to_bool, get_neo4j_node, create_story_query, story_flow, format_story_results)

api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/about')
def about():
    """
    Display general information about the app.

    :rtype: flask.Response
    """
    return jsonify({'version': version})


@api_v1.route('/<resource>/<uid>')
def get_resource(resource, uid):
    """
    Get a resource from Neo4j.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource was requested
    """
    # Default the relationship flag to True
    relationship = True
    if request.args.get('relationship'):
        relationship = str_to_bool(request.args['relationship'])

    item = get_neo4j_node(resource, uid)
    if not item:
        raise NotFound('This item does not exist')

    if relationship:
        return jsonify(item.serialized_all)
    else:
        return jsonify(item.serialized)


@api_v1.route('/story')
def get_available_resources():
    """
    List the available resources and their unique ID property.

    :return: a Flask JSON response
    :rtype: flask.Response
    """
    return jsonify({label.lower(): story_flow(label)['uid_name'] for label in story_flow_list})


@api_v1.route('/story/<resource>/<uid>')
def get_resource_story(resource, uid):
    """
    Get the story of a resource from Neo4j.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource was requested
    """
    item = get_neo4j_node(resource, uid)
    if not item:
        raise NotFound('This item does not exist')

    forward_query = create_story_query(item, item.id, limit=True)
    backward_query = create_story_query(item, item.id, reverse=True, limit=True)

    def _get_partial_story(query, reverse=False):
        results, _ = db.cypher_query(query)

        if not results:
            return []

        # Assuming that if Path is the first result, then that's all we want to process
        results = [list(results[0][0].nodes)]
        # Reverse will be true when it is a backward query to preserve the story order
        if reverse:
            results = [results[0][::-1]]

        return EstuaryStructuredNode.inflate_results(results)[0]

    results = []
    if forward_query:
        results = _get_partial_story(forward_query)

    if backward_query:
        backward_query_results = _get_partial_story(backward_query, reverse=True)
        if backward_query_results and results:
            # Remove the first element of backward_query_results in order to avoid
            # duplication of the requested resource when result of forward query are not None.
            backward_query_results = backward_query_results[:-1]
        results = backward_query_results + results

    # Adding the artifact itself if it's story is not available
    if not results:
        rv = {'data': [item.serialized_all], 'meta': {}}
        rv['meta']['story_related_nodes'] = [0]
        rv['data'][0]['resource_type'] = item.__label__
        return jsonify(rv)

    return jsonify(format_story_results(results, item))


@api_v1.route('/allstories/<resource>/<uid>')
def get_resource_all_stories(resource, uid):
    """
    Get all unique stories of an artifact from Neo4j.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource was requested
    """
    item = get_neo4j_node(resource, uid)
    if not item:
        raise NotFound('This item does not exist')

    forward_query = create_story_query(item, item.id)
    backward_query = create_story_query(item, item.id, reverse=True)

    def _get_partial_stories(query, reverse=False):

        results_list = []
        results, _ = db.cypher_query(query)

        if not results:
            return results_list

        # Creating a list of lists where each list is a collection of node IDs
        # of the nodes present in that particular story path.
        # Paths are re-sorted in ascending order to simplify the logic below
        path_nodes_id = []
        for path in reversed(results):
            path_nodes_id.append([node.id for node in path[0].nodes])

        unique_paths = []
        for index, node_set in enumerate(path_nodes_id[:-1]):
            unique = True
            for alternate_set in path_nodes_id[index + 1:]:
                # If the node_set is a subset of alternate_set,
                # we know they are the same path except the alternate_set is longer.
                # If alternate_set and node_set only have one node ID of difference,
                # we know it's the same path but from the perspective of different siblings.
                if set(node_set).issubset(set(alternate_set)) or len(
                        set(alternate_set).difference(set(node_set))) == 1:
                    unique = False
                    break
            if unique:
                # Since results is from longest to shortest, we need to get the opposite index.
                unique_paths.append(results[(len(path_nodes_id) - index) - 1][0])
        # While traversing, the outer for loop only goes until the second to last element
        # because the inner for loop always starts one element ahead of the outer for loop.
        # Hence, all the subsets of the last element will not be added to the unique_paths
        # list as the for loops will eliminate them. So we add the last element
        # since we are sure it is unique.
        unique_paths.append(results[0][0])
        if reverse:
            unique_paths_nodes = [path.nodes[::-1] for path in unique_paths]
        else:
            unique_paths_nodes = [path.nodes for path in unique_paths]

        return EstuaryStructuredNode.inflate_results(unique_paths_nodes)

    if forward_query:
        results_forward = _get_partial_stories(forward_query)
    else:
        results_forward = []

    if backward_query:
        results_backward = _get_partial_stories(backward_query, reverse=True)
    else:
        results_backward = []

    all_results = []
    if not results_backward or not results_forward:
        if results_forward:
            results_unidir = results_forward
        else:
            results_unidir = results_backward

        for result in results_unidir:
            all_results.append(format_story_results(result, item))

    else:
        # Combining all the backward and forward paths to generate all the possible full paths
        for result_forward in results_forward:
            for result_backward in results_backward:
                results = result_backward + result_forward[1:]
                all_results.append(format_story_results(results, item))

    # Adding the artifact itself if its story is not available
    if not all_results:
        rv = {'data': [item.serialized_all], 'meta': {}}
        rv['meta']['story_related_nodes'] = [0]
        rv['data'][0]['resource_type'] = item.__label__
        all_results.append(rv)

    return jsonify(all_results)
