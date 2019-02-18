# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import NotFound

from estuary import version
from estuary.models.base import EstuaryStructuredNode

from estuary.utils.general import str_to_bool, get_neo4j_node, inflate_node, login_required
from estuary.utils.recents import get_recent_nodes
from estuary.error import ValidationError
import estuary.utils.story


api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/about')
def about():
    """
    Display general information about the app.

    :rtype: flask.Response
    """
    return jsonify({
        'auth_required': current_app.config['ENABLE_AUTH'],
        'version': version
    })


@api_v1.route('/<resource>/<uid>')
@login_required
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


@api_v1.route('/story/<resource>/<uid>')
@login_required
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
    fallback_resources = request.args.getlist('fallback')
    # Try all resources input by the user
    for _resource in [resource] + fallback_resources:
        item = get_neo4j_node(_resource, uid)
        # If a resource is found, we don't need to try the other resources
        if item:
            break

    if not item:
        raise NotFound('This item does not exist')

    story_manager = estuary.utils.story.BaseStoryManager.get_story_manager(
        item, current_app.config, limit=True)

    def _get_partial_story(results, reverse=False):

        if not results:
            return []

        # Assuming that if Path is the first result, then that's all we want to process
        results = [list(results[0][0].nodes)]
        # Reverse will be true when it is a backward query to preserve the story order
        if reverse:
            results = [results[0][::-1]]

        return EstuaryStructuredNode.inflate_results(results)[0]

    results = []
    if story_manager.forward_story:
        results = story_manager.set_story_labels(item.__label__, _get_partial_story(
            story_manager.forward_story))

    if story_manager.backward_story:
        backward_query_results = story_manager.set_story_labels(
            item.__label__, _get_partial_story(
                story_manager.backward_story, reverse=True), reverse=True)
        if backward_query_results and results:
            # Remove the first element of backward_query_results in order to avoid
            # duplication of the requested resource when result of forward query are not None.
            backward_query_results = backward_query_results[:-1]
        results = backward_query_results + results

    # Adding the artifact itself if it's story is not available
    if not results:
        rv = {'data': [item.serialized_all], 'meta': {}}
        rv['meta']['story_related_nodes_forward'] = [0]
        rv['meta']['story_related_nodes_backward'] = [0]
        rv['meta']['requested_node_index'] = 0
        rv['meta']['story_type'] = story_manager.__class__.__name__[:-12].lower()
        rv['data'][0]['resource_type'] = item.__label__
        rv['data'][0]['display_name'] = item.display_name
        return jsonify(rv)

    return jsonify(story_manager.format_story_results(results, item))


@api_v1.route('/allstories/<resource>/<uid>')
@login_required
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
    fallback_resources = request.args.getlist('fallback')
    # Try all resources input by the user
    for _resource in [resource] + fallback_resources:
        item = get_neo4j_node(_resource, uid)
        # If a resource is found, we don't need to try the other resources
        if item:
            break

    story_manager = estuary.utils.story.BaseStoryManager.get_story_manager(item, current_app.config)

    def _get_partial_stories(results, reverse=False):

        results_list = []

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

    if story_manager.forward_story:
        results_forward = _get_partial_stories(story_manager.forward_story)
    else:
        results_forward = []

    if story_manager.backward_story:
        results_backward = _get_partial_stories(story_manager.backward_story, reverse=True)
    else:
        results_backward = []

    all_results = []
    if not results_backward or not results_forward:
        if results_forward:
            results_unidir = [story_manager.set_story_labels(
                item.__label__, result) for result in results_forward]
        else:
            results_unidir = [story_manager.set_story_labels(
                item.__label__, result, reverse=True) for result in results_backward]

        for result in results_unidir:
            all_results.append(story_manager.format_story_results(result, item))

    else:
        # Combining all the backward and forward paths to generate all the possible full paths
        for result_forward in results_forward:
            for result_backward in results_backward:
                results = story_manager.set_story_labels(
                    item.__label__, result_backward, reverse=True) + \
                    story_manager.set_story_labels(item.__label__, result_forward)[1:]
                all_results.append(story_manager.format_story_results(results, item))

    # Adding the artifact itself if its story is not available
    if not all_results:
        rv = {'data': [item.serialized_all], 'meta': {}}
        rv['meta']['story_related_nodes_forward'] = [0]
        rv['meta']['story_related_nodes_backward'] = [0]
        rv['meta']['requested_node_index'] = 0
        rv['meta']['story_type'] = story_manager.__class__.__name__[:-12].lower()
        rv['data'][0]['resource_type'] = item.__label__
        rv['data'][0]['display_name'] = item.display_name
        all_results.append(rv)

    return jsonify(all_results)


@api_v1.route('/siblings/<resource>/<uid>')
@login_required
def get_siblings(resource, uid):
    """
    Get siblings of next/previous node that are correlated to the node in question.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource was requested
    """
    story_type_mapper = {'container': 'ContainerStoryManager', 'module': 'ModuleStoryManager'}
    story_type = request.args.get('story_type', 'container').lower()

    story_manager_class = story_type_mapper.get(story_type)
    if story_manager_class:
        story_manager = getattr(estuary.utils.story, story_manager_class)()
    else:
        raise ValidationError('Supplied story type is invalid. Select from: {0}'
                              .format(', '.join(current_app.config['STORY_MANAGER_SEQUENCE'])))

    # This is the node that is part of a story which has the relationship to the desired
    # sibling nodes
    story_node = get_neo4j_node(resource, uid)
    if not story_node:
        raise NotFound('This item does not exist')

    story_node_story_flow = story_manager.story_flow(story_node.__label__)
    # If backward_rel is true, we fetch siblings of the previous node, next node otherwise.
    # For example, if you pass in an advisory and want to know the Freshmaker events triggered from
    # that advisory, backward_rel would be false. If you want to know the Koji builds attached to
    # that advisory, then backward_rel would true.
    backward = str_to_bool(request.args.get('backward_rel'))
    if backward and story_node_story_flow['backward_label']:
        desired_siblings_label = story_node_story_flow['backward_label']
    elif not backward and story_node_story_flow['forward_label']:
        desired_siblings_label = story_node_story_flow['forward_label']
    else:
        raise ValidationError('Siblings cannot be determined on this kind of resource')

    sibling_nodes = story_manager.get_sibling_nodes(desired_siblings_label, story_node)
    # Inflating and formatting results from Neo4j
    serialized_results = []
    for result in sibling_nodes:
        inflated_node = inflate_node(result[0])
        serialized_node = inflated_node.serialized_all
        serialized_node['resource_type'] = inflated_node.__label__
        serialized_node['display_name'] = inflated_node.display_name
        serialized_results.append(serialized_node)

    description = story_manager.get_siblings_description(
        story_node.display_name, story_node_story_flow, backward)

    result = {
        'data': serialized_results,
        'meta': {
            'description': description
        }
    }

    return jsonify(result)


@api_v1.route('/relationships/<resource>/<uid>/<relationship>')
@login_required
def get_artifact_relationships(resource, uid, relationship):
    """
    Get one-to-many relationships of a particular artifact.

    :param str resource: a resource name that maps to a neomodel class
    :param str uid: the value of the UniqueIdProperty to query with
    :param str relationship: relationship to expand
    :return: a Flask JSON response
    :rtype: flask.Response
    :raises NotFound: if the item is not found
    :raises ValidationError: if an invalid resource/relationship was requested
    """
    item = get_neo4j_node(resource, uid)
    if not item:
        raise NotFound('This item does not exist')

    if relationship not in [rel[0] for rel in item.__all_relationships__]:
        raise ValidationError(
            'Please provide a valid relationship name for {0} with uid {1}'.format(resource, uid))

    rel_display_name = relationship.replace('_', ' ')
    results = {
        'data': [],
        'meta': {
            'description': '{0} of {1}'.format(rel_display_name, item.display_name)
        }
    }

    related_nodes = getattr(item, relationship).match()
    for node in related_nodes:
        serialized_node = node.serialized_all
        serialized_node['resource_type'] = node.__label__
        serialized_node['display_name'] = node.display_name
        results['data'].append(serialized_node)

    return jsonify(results)


@api_v1.route('/recents')
@login_required
def get_recent_stories():
    """Get stories that were most recently updated, by their artifact type."""
    nodes = get_recent_nodes()
    result = {
        'data': nodes,
        'metadata': {}
    }

    return jsonify(result)
