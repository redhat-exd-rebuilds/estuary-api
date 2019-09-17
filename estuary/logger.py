# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import logging
import sys


# Inspired from waiverdb
def log_to_stdout(level=logging.INFO):
    """
    Configure loggers to stream to STDOUT.

    :param int level: the logging level
    """
    fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    datefmt = '%Y-%m-%d %H:%M:%S'
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    logging.getLogger().addHandler(stream_handler)


def init_logging(app):
    """
    Initialize logging on the Flask application.

    :param flask.Flask app: a Flask application object
    """
    log_to_stdout(level=app.config['LOG_LEVEL'])
    # In general we want to see everything from our own code,
    # but not detailed debug messages from third-party libraries.
    # Note that the log level on the handler above controls what
    # will actually appear on stdout.
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger('estuary').setLevel(logging.DEBUG)
