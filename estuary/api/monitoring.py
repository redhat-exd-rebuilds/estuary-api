# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import time

from flask import Response, Blueprint, request
import prometheus_client


REQUEST_COUNT = prometheus_client.Counter(
    'request_count', 'App Request Count',
    ['app_name', 'method', 'endpoint', 'query_string', 'http_status'])

REQUEST_LATENCY = prometheus_client.Histogram(
    'request_latency_seconds', 'Request latency',
    ['app_name', 'endpoint', 'query_string'])


def start_request_timer():
    """Start the request timer."""
    request.start_time = time.time()


def stop_request_timer(response):
    """
    Stop the request timer.

    :param flask.Response response: the Flask response to stop the timer on
    :return: the Flask response
    :rtype: flask.Response
    """
    resp_time = time.time() - request.start_time
    REQUEST_LATENCY.labels(
        'estuary-api', request.path, request.query_string.decode('utf-8')).observe(resp_time)
    return response


def record_request_metadata(response):
    """
    Record metadata about the request.

    :param flask.Response response: the Flask response to record metadata about
    :return: the Flask response
    :rtype: flask.Response
    """
    REQUEST_COUNT.labels(
        'estuary-api', request.method, request.path, request.query_string,
        response.status_code).inc()
    return response


def configure_monitoring(app):
    """Configure monitoring on the Flask app.

    :param flask.Flask app: the Flask application to configure
    """
    app.before_request(start_request_timer)
    app.after_request(stop_request_timer)
    app.after_request(record_request_metadata)


monitoring_api = Blueprint('monitoring', __name__)


@monitoring_api.route('/metrics')
def metrics():
    """
    Display Prometheus metrics about the app.

    :rtype: flask.Response
    """
    return Response(
        prometheus_client.generate_latest(),
        content_type=prometheus_client.CONTENT_TYPE_LATEST)
