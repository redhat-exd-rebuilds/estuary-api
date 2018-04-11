# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from datetime import datetime

from neomodel import StructuredNode


class PurviewStructuredNode(StructuredNode):
    __abstract_node__ = True

    @property
    def serialized(self):
        rv = self.__properties__
        # Remove the Neo4j internal ID
        del rv['id']
        # "id_" is actually the node's ID from the source
        if 'id_' in rv:
            # Rename as "id" for clarity
            rv['id'] = rv['id_']
            del rv['id_']

        for key, value in self.__properties__.items():
            if isinstance(value, datetime):
                rv[key] = value.isoformat()

        return rv
