# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import current_app


def is_user_authorized(employee_type):
    """
    Verify the user is authorized to access the application.

    :param str employee_type: the employee type from the user's token
    :return: a boolean that determines if the user is authorized
    :rtype: bool
    """
    employee_types = current_app.config.get('EMPLOYEE_TYPES', [])
    # If the application is configured to only allow employees, perform the verification
    return not employee_types or employee_type in employee_types
