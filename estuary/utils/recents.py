# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from neomodel import db
from estuary.models.koji import KojiBuild
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitCommit
from estuary.models.errata import Advisory
from estuary.models.freshmaker import FreshmakerEvent

from estuary.utils.general import inflate_node


def get_recent_nodes():
    """
    Get the most recent nodes of each node type.

    :return: a dictionary with the keys as names of each node type, and
        values of arrays of the most recents of each node
    :rtype: dict
    """
    label_dict = {
        FreshmakerEvent.__label__: 'id',
        BugzillaBug.__label__: 'modified_time',
        DistGitCommit.__label__: 'commit_date',
        KojiBuild.__label__: 'completion_time',
        Advisory.__label__: 'update_date'
    }

    final_result = {}
    for label, time_property in label_dict.items():
        query = (
            'MATCH (node:{label}) '
            'WHERE node.{time_property} IS NOT NULL '
            'RETURN node '
            'ORDER BY node.{time_property} DESC LIMIT 5'
        ).format(label=label, time_property=time_property)
        results, _ = db.cypher_query(query)
        for result in results:
            node_results = final_result.setdefault(label, [])
            # result is always a list of a single node
            node = inflate_node(result[0])
            node_results.append(node.serialized)

    return final_result
