# SPDX-License-Identifier: GPL-3.0+
# Inspired from the MARS project

from __future__ import unicode_literals

from time import sleep

import psycopg2

from purview import log


class Teiid(object):
    """Abstracts interfacing with TEIID to simplify connections and queries."""

    def __init__(self, host, port, username, password):
        """
        Initialize the Teiid class.

        :param str host: the TEIID FQDN or IP address
        :param int port: the port to connect to TEIID with
        :param str username: the username to connect to TEIID with
        :param str password: the password to connect to TEIID with
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # a dict mapping db names to cursors
        self._connections = {}

    def get_connection(self, db_name, force_new=False, retry=None):
        """
        Return an existing psycopg2 connection and establish it if needed.

        :param str db_name: the database name to get a connection to
        :kwarg bool force_new: forces a new database connection even if one
        already exists
        :kwarg int retry: the number of times to retry a failed connection. If this
        is not set, then the TEIID connection attempt will be repeated until it is successful.
        :return: a connection to TEIID
        :rtype: psycopg2 connection
        """
        if not force_new and db_name in self._connections:
            return self._connections[db_name]
        if retry is not None and retry < 1:
            raise ValueError('The retry keyword must contain a value greater than 0')

        log.debug('Connecting to Teiid host {0}:{1}'.format(self.host, self.port))
        attempts = 0
        while True:
            attempts += 1
            try:
                conn = psycopg2.connect(
                    database=db_name,
                    host=self.host,
                    port=str(self.port),
                    user=self.username,
                    password=self.password,
                    connect_timeout=60
                )
                break
            except psycopg2.OperationalError:
                if retry and attempts > retry:
                    raise
                else:
                    log.warning('The Teiid connection failed on attempt {0}. Sleeping for 60 '
                                'seconds.'.format(attempts))
                    sleep(60)

        # Teiid does not support setting this value at all and unless we
        # specify ISOLATION_LEVEL_AUTOCOMMIT (zero), psycopg2 will send a
        # SET command to the Teiid server doesn't understand.
        conn.set_isolation_level(0)

        self._connections[db_name] = conn
        return conn

    def query(self, sql, db='public', retry=None):
        """
        Send the SQL query to Teiid and return the rows as a list.

        :param str sql: the SQL query to send to the database
        :kwarg str db: the database name to query on
        :kwarg int retry: the number of times to retry a failed query. If this
        is not set, then the TEIID query will be repeated until it is successful.
        :return: a list of rows from Teiid. Each row is a dictionary
        with the column headers as the keys.
        :rtype: list
        """
        con = self.get_connection(db)
        cursor = con.cursor()
        if retry is not None and retry < 1:
            raise ValueError('The retry keyword must contain a value greater than 0')

        log.debug('Querying Teiid DB "{0}" with SQL:\n{1}'.format(db, sql))

        fifteen_mins = 15 * 60
        backoff = 30
        attempts = 0
        while True:
            attempts += 1
            try:
                if attempts > 1:
                    # Restart the database connection after failed queries
                    con = self.get_connection(db, force_new=True)
                cursor.execute(sql)
                break
            except psycopg2.OperationalError:
                if retry and attempts > retry:
                    raise
                else:
                    if backoff < fifteen_mins:
                        # Double the backoff time
                        backoff = backoff * 2
                    elif backoff > fifteen_mins:
                        # Max out the backoff time to 15 minutes
                        backoff = fifteen_mins
                    log.warning('The Teiid query failed on attempt {0}. Sleeping for {1} seconds.'
                                .format(attempts, backoff))
                    sleep(backoff)

        data = cursor.fetchall()
        # column header names
        cols = [t[0] for t in cursor.description or []]
        log.debug('Found the following columns: {}'.format(cols))
        log.debug('Received {} rows from Teiid'.format(len(data)))
        # build a return array with all columns
        return [dict(zip(cols, row)) for row in data]
