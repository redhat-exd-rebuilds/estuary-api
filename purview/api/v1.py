# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import NotFound
from neomodel import UniqueIdProperty

from purview import version
from purview.models import all_models
from purview.error import ValidationError
from purview.utils.general import str_to_bool

api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/about')
def about():
    """
    Display version info about purview
    :return: A JSON object with version info
    """
    return jsonify({'version': version})


@api_v1.route('/<resource>/<uid>')
def get_resource(resource, uid):
    # Default the relationship flag to True
    relationship = True
    if request.args.get('relationship'):
        relationship = str_to_bool(request.args['relationship'])

    for model in all_models:
        if model.__name__.lower() == resource:
            for prop_name, prop_def in model.defined_properties().items():
                if isinstance(prop_def, UniqueIdProperty):
                    item = model.nodes.get_or_none(**{prop_def.name: uid})
                    if not item:
                        raise NotFound('This item does not exist')

                    if relationship is False:
                        return jsonify(item.serialized)

                    serialized = item.serialized
                    for relationship_name, _ in item.__all_relationships__:
                        serialized[relationship_name] = [
                            obj.serialized for obj in getattr(item, relationship_name).all()]
                    return jsonify(serialized)

    # Some models don't have unique ID's and those should be skipped
    models_wo_uid = ('DistGitRepo', 'DistGitBranch')
    model_names = [model.__name__.lower() for model in all_models
                   if model.__name__ not in models_wo_uid]
    error = ('The requested resource "{0}" is invalid. Choose from the following: '
             '{1}, and {2}.'.format(resource, ', '.join(model_names[:-1]), model_names[-1]))
    raise ValidationError(error)
