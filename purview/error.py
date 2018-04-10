# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import jsonify
from werkzeug.exceptions import HTTPException
from neo4j.exceptions import ServiceUnavailable, AuthError


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
        message = None
        if isinstance(error, ValidationError):
            status_code = 400
        elif isinstance(error, ServiceUnavailable) or isinstance(error, AuthError):
            status_code = 503
            message = 'The database connection failed'

        response = jsonify({
            'status': status_code,
            'message': message or str(error)
        })
        response.status_code = status_code
    return response
