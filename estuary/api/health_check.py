# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import db

from estuary import log


def health_check():
    """Determine the health of the API by checking if the database interactions are working."""
    msg = 'Health check OK'
    status = 200
    try:
        # Just perform a simple math operation that doesn't rely on any data being present in the
        # database
        results, _ = db.cypher_query('RETURN sqrt(4)')
        assert results[0][0] == 2.0
    except:  # noqa E722
        log.exception('An exception was encountered when verifying the database connection in the '
                      'health check API endpoint')
        msg = 'The health check failed while verifying the database connection'
        status = 503

    return (msg, status, [('Content-Type', 'text/plain')])
