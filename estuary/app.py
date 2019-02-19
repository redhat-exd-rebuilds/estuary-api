# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import os
import warnings

from flask import Flask, current_app, request
from werkzeug.exceptions import default_exceptions
from neomodel import config as neomodel_config
from neo4j.exceptions import ServiceUnavailable, AuthError

from estuary import log
from estuary.logger import init_logging
from estuary.error import json_error, ValidationError
from estuary.api.v1 import api_v1


def load_config(app):
    """
    Determine the correct configuration to use and apply it.

    :param flask.Flask app: a Flask application object
    """
    default_config_file = None
    if os.getenv('DEV') and os.getenv('DEV').lower() == 'true':
        default_config_obj = 'estuary.config.DevConfig'
    else:
        default_config_obj = 'estuary.config.ProdConfig'
        default_config_file = '/etc/estuary/settings.py'

    app.config.from_object(default_config_obj)
    config_file = os.environ.get('ESTUARY_CONFIG', default_config_file)
    if config_file and os.path.isfile(config_file):
        app.config.from_pyfile(config_file)

    if os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    if os.environ.get('NEO4J_URI'):
        app.config['NEO4J_URI'] = os.environ['NEO4J_URI']
    if os.environ.get('ENABLE_AUTH', '').lower() == 'true':
        app.config['ENABLE_AUTH'] = True
    elif os.environ.get('ENABLE_AUTH', '').lower() == 'false':
        app.config['ENABLE_AUTH'] = False
    elif os.environ.get('ENABLE_AUTH'):
        warnings.warn(
            'The value of the environment variable "ENABLE_AUTH" is invalid and will be ignored')
    if os.environ.get('OIDC_INTROSPECT_URL'):
        app.config['OIDC_INTROSPECT_URL'] = os.environ['OIDC_INTROSPECT_URL']
    if os.environ.get('OIDC_CLIENT_ID'):
        app.config['OIDC_CLIENT_ID'] = os.environ['OIDC_CLIENT_ID']
    if os.environ.get('OIDC_CLIENT_SECRET'):
        app.config['OIDC_CLIENT_SECRET'] = os.environ['OIDC_CLIENT_SECRET']
    if os.environ.get('CORS_ORIGINS'):
        app.config['CORS_ORIGINS'] = os.environ['CORS_ORIGINS'].split(',')


def insert_headers(response):
    """
    Insert configured HTTP headers into the Flask response.

    :param flask.Response response: the response to insert headers into
    :return: modified Flask response
    :rtype: flask.Response
    """
    cors_origins = current_app.config.get('CORS_ORIGINS', [])
    origin = request.headers.get('Origin')
    if origin and origin in cors_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Method'] = 'GET, OPTIONS'
    return response


def create_app(config_obj=None):
    """
    Create a Flask application object.

    :return: a Flask application object
    :rtype: flask.Flask
    """
    app = Flask(__name__)
    if config_obj:
        app.config.from_object(config_obj)
    else:
        load_config(app)

    if app.config['PRODUCTION'] and app.secret_key == 'replace-me-with-something-random':
        raise RuntimeError('You need to change the app.secret_key value for production')
    elif app.config['ENABLE_AUTH']:
        base_error = 'The "{0}" configuration must be set if authentication is enabled'
        if not app.config['OIDC_INTROSPECT_URL']:
            raise RuntimeError(base_error.format('OIDC_INTROSPECT_URL'))
        elif not app.config['OIDC_CLIENT_ID']:
            raise RuntimeError(base_error.format('OIDC_CLIENT_ID'))
        elif not app.config['OIDC_CLIENT_SECRET']:
            raise RuntimeError(base_error.format('OIDC_CLIENT_SECRET'))

    # Set the Neo4j connection URI based on the Flask config
    neomodel_config.DATABASE_URL = app.config.get('NEO4J_URI')

    if app.config['ENABLE_AUTH']:
        # Import this here so that flask_oidc isn't required to run the app if authentication is
        # disabled
        from estuary.auth import EstuaryOIDC
        app.oidc = EstuaryOIDC(app)

    init_logging(app)

    for status_code in default_exceptions.keys():
        app.register_error_handler(status_code, json_error)
    app.register_error_handler(ValidationError, json_error)
    app.register_error_handler(ServiceUnavailable, json_error)
    app.register_error_handler(AuthError, json_error)
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    try:
        from estuary.api.monitoring import monitoring_api, configure_monitoring
        app.register_blueprint(monitoring_api, url_prefix='/monitoring')
        configure_monitoring(app)
    except ImportError as e:
        # If prometheus_client isn't installed, then don't register the monitoring blueprint
        log.warning('The promethus_client is not installed, so metrics will be disabled')
        if 'prometheus_client' not in str(e):
            raise

    app.after_request(insert_headers)

    return app
