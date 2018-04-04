# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import jsonify, Blueprint

from purview import version


api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/about')
def about():
    """
    Display version info about purview
    :return: A JSON object with version info
    """
    return jsonify({'version': version})
