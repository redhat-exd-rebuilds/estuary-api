# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import jsonify
from werkzeug.exceptions import HTTPException


class ValidationError(ValueError):
    pass


def json_error(error):
    """
    Converts exceptions to JSON responses
    :param: an Exception object
    :return: a JSON response
    """
    if isinstance(error, HTTPException):
        response = jsonify({
            'status': error.code,
            'message': error.description
        })
        response.status_code = error.code
    else:
        status_code = 500
        if isinstance(error, ValidationError):
            status_code = 400
        response = jsonify({
            'status': status_code,
            'message': str(error)
        })
        response.status_code = status_code
    return response
