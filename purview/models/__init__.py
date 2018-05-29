# SPDX-License-Identifier: GPL-3.0+

from neomodel import RelationshipManager
from neomodel.relationship_manager import check_source, _rel_helper

from purview.models.koji import ContainerKojiBuild, KojiBuild, KojiTask, KojiTag
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitRepo, DistGitPush, DistGitBranch, DistGitCommit
from purview.models.errata import Advisory, AdvisoryState
from purview.models.freshmaker import FreshmakerEvent
from purview.models.user import User

all_models = (Advisory, AdvisoryState, BugzillaBug, ContainerKojiBuild, DistGitBranch,
              DistGitCommit, DistGitPush, DistGitRepo, FreshmakerEvent, KojiBuild,
              KojiTag, KojiTask, User)
names_to_model = {model.__label__: model for model in all_models}
story_flow_list = ['BugzillaBug', 'DistGitCommit', 'KojiBuild',
                   'Advisory', 'FreshmakerEvent', 'ContainerKojiBuild']

# Overrides from https://github.com/neo4j-contrib/neomodel/pull/327
# These should be removed once a new version is released
@check_source
def disconnect_all(self):   # pragma: no cover
    """Add the disconnect_all method from PR #327."""
    rhs = 'b:' + self.definition['node_class'].__label__
    rel = _rel_helper(lhs='a', rhs=rhs, ident='r', **self.definition)
    q = 'MATCH (a) WHERE id(a)={self} MATCH ' + rel + ' DELETE r'
    self.source.cypher(q)


@check_source
def replace(self, node, properties=None):   # pragma: no cover
    """Add the replace method from PR #327."""
    self.disconnect_all()
    self.connect(node, properties)


RelationshipManager.disconnect_all = disconnect_all
RelationshipManager.replace = replace
