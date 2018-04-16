# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from datetime import datetime
from six import text_type

from purview import log


def timestamp_to_datetime(timestamp):
    """
    Convert a string timestamp to a datetime object.

    :param str timestamp: a generic or ISO-8601 timestamp
    :return: datetime object of the timestamp
    :rtype: datetime.datetime
    :raises ValueError: if the timestamp is an unsupported or invalid format
    """
    log.debug('Trying to parse the timestamp "{0}"'.format(timestamp))
    error_msg = 'The timestamp "{0}" is an invalid format'.format(timestamp)
    combinations = (
        (r'^(?P<datetime>\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2})(?:\.\d+)?$',
         '%Y-%m-%d %H:%M:%S'),
        (r'^(?P<datetime>\d{4}-\d{1,2}-\d{1,2})$', '%Y-%m-%d'),
        # ISO 8601 format
        (r'^(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.\d+)?(?:Z|[-+]00(?::00)?)?$',
         '%Y-%m-%dT%H:%M:%S'))

    for combination in combinations:
        regex_match = re.match(combination[0], timestamp)
        if regex_match:
            try:
                return datetime.strptime(regex_match.group('datetime'), combination[1])
            except ValueError:
                # In case the user asked for an unreleastic date like "2020:99:99"
                raise ValueError(error_msg)

    raise ValueError(error_msg)


def str_to_bool(item):
    """
    Convert a string to a boolean.

    :param str item: string to parse
    :return: a boolean equivalent
    :rtype: boolean
    """
    if isinstance(item, text_type):
        return item.lower() in ('true', '1')
    else:
        return False


def inflate_node(result):
    """
    Inflate a Neo4j result to a neomodel model object.

    :param neo4j.v1.types.Node result: a node from a cypher query result
    :return: a model (PurviewStructuredNode) object
    """
    # To prevent a ciruclar import, this must be imported here
    from purview.models import names_to_model

    for label in result.labels:
        if label in names_to_model:
            node_model = names_to_model[label]
            break
    else:
        # This should never happen unless Neo4j returns labels that aren't associated with
        # classes in all_models
        RuntimeError('A StructuredNode couldn\'t be found from the labels: {0}'.format(
            ', '.join(result.labels)))

    return node_model.inflate(result)
