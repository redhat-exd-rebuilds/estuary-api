# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from datetime import datetime

from six import text_type

from estuary import log
from estuary.error import ValidationError


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


def timestamp_to_date(timestamp):
    """
    Convert a string timestamp to a date object.

    :param str timestamp: a generic or ISO-8601 timestamp
    :return: date object of the timestamp
    :rtype: datetime.date
    :raises ValueError: if the timestamp is an unsupported or invalid format
    """
    return timestamp_to_datetime(timestamp).date()


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
    :return: a model (EstuaryStructuredNode) object
    """
    # To prevent a ciruclar import, this must be imported here
    from estuary.models import names_to_model

    if 'ContainerKojiBuild' in result.labels:
        result_label = 'ContainerKojiBuild'
    elif 'ContainerAdvisory' in result.labels:
        result_label = 'ContainerAdvisory'
    elif 'ModuleKojiBuild' in result.labels:
        result_label = 'ModuleKojiBuild'
    elif len(result.labels) > 1:
        raise RuntimeError('inflate_node encounted a node with multiple labels: {0}. '
                           'Which one should be used?'.format(', '.join(result.labels)))
    else:
        result_label = list(result.labels)[0]

    if result_label in names_to_model:
        node_model = names_to_model[result_label]
    else:
        # This should never happen unless Neo4j returns labels that aren't associated with
        # classes in all_models
        raise RuntimeError('A StructuredNode couldn\'t be found from the labels: {0}'.format(
            ', '.join(result.labels)))

    return node_model.inflate(result)


def get_neo4j_node(resource_name, uid):
    """
    Get a Neo4j node based on a label and unique identifier.

    :param str resource_name: a neomodel model label
    :param str uid: a string of the unique identifier defined in the neomodel model
    :return: a neomodel model object
    :raises ValidationError: if the requested resource doesn't exist or doesn't have a
    UniqueIdProperty
    """
    # To prevent a ciruclar import, we must import this here
    from estuary.models import all_models

    for model in all_models:
        if model.__label__.lower() == resource_name.lower():
            try:
                return model.find_or_none(uid)
            except RuntimeError:
                # There is no UniqueIdProperty on this model so raise an exception
                models_wo_uid = ('DistGitRepo', 'DistGitBranch')
                model_names = [model.__name__.lower() for model in all_models
                               if model.__name__ not in models_wo_uid]
                error = ('The requested resource "{0}" is invalid. Choose from the following: '
                         '{1}, and {2}.'.format(resource_name, ', '.join(model_names[:-1]),
                                                model_names[-1]))
                raise ValidationError(error)
