# SPDX-License-Identifier: GPL-3.0+
# Inspired from the MARS project

from __future__ import unicode_literals

import psycopg2

from purview import log


class Teiid(object):

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # a dict mapping db names to cursors
        self._connections = {}

    def get_connection(self, db_name):
        """
        Return an existing psycopg2 connection and establish it if needed
        :arg db_name: a string of the database name to get a connection to
        :return: a psycopg2 connection
        """
        if db_name in self._connections:
            return self._connections[db_name]

        log.debug('Connecting to Teiid host {0}:{1}'.format(
            self.host, self.port))
        conn = psycopg2.connect(
            database=db_name,
            host=self.host,
            port=str(self.port),
            user=self.username,
            password=self.password,
        )

        # Teiid does not support setting this value at all and unless we
        # specify ISOLATION_LEVEL_AUTOCOMMIT (zero), psycopg2 will send a
        # SET command to the Teiid server doesn't understand.
        conn.set_isolation_level(0)

        self._connections[db_name] = conn
        return conn

    def query(self, sql, db='public', retry=3):
        """
        Send the SQL query to Teiid and return the rows as a list
        :param sql: a string of the SQL query to send to the database
        :kwarg db: the database name to query on
        :kwarg retry: an int of the  number of times to retry a failed query
        :return: a list of rows from Teiid. Each row is a dictionary
        with the column header as the key.
        """
        con = self.get_connection(db)
        cursor = con.cursor()

        log.debug('Querying Teiid DB "{0}" with SQL:\n{1}'.format(db, sql))

        for _ in range(retry):
            try:
                cursor.execute(sql)
                break
            except psycopg2.extensions.QueryCanceledError as err:
                log.warning('Teiid query failed')
        else:
            raise err  # noqa: F821

        data = cursor.fetchall()
        # column header names
        cols = [t[0] for t in cursor.description or []]
        log.debug('Found the following columns: {}'.format(cols))
        log.debug('Received {} rows from Teiid'.format(len(data)))
        # build a return array with all columns
        return [dict(zip(cols, row)) for row in data]
