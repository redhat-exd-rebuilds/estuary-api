# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import NotFound

from purview import version
from purview.utils.general import str_to_bool, get_neo4j_node

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
