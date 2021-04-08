# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import jsonify
from neo4j.exceptions import AuthError, ServiceUnavailable
from werkzeug.exceptions import HTTPException

from estuary import log


class ValidationError(ValueError):
    """A custom exception handled by Flask to denote bad user input."""

    pass


def json_error(error):
    """
    Convert exceptions to JSON responses.

    :param Exception error: an Exception to convert to JSON
    :return: a Flask JSON response
    :rtype: flask.Response
    """
    if isinstance(error, HTTPException):
        response = jsonify({
            'status': error.code,
            'message': error.description
        })
        response.status_code = error.code
    else:
        # Log the actual exception before it's gobbled up by Flask
        log.exception(error)
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
