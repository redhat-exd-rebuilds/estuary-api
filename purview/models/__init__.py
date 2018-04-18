# SPDX-License-Identifier: GPL-3.0+

from neomodel import RelationshipManager
from neomodel.relationship_manager import check_source, _rel_helper

from purview.models.koji import KojiBuild, KojiTask, KojiTag
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitRepo, DistGitPush, DistGitBranch, DistGitCommit
from purview.models.errata import Advisory, AdvisoryState
from purview.models.freshmaker import FreshmakerEvent, ContainerBuilds
from purview.models.user import User

all_models = (Advisory, AdvisoryState, BugzillaBug, ContainerBuilds, DistGitBranch,
              DistGitCommit, DistGitPush, DistGitRepo, FreshmakerEvent, KojiBuild,
              KojiTag, KojiTask, User)
names_to_model = {model.__label__: model for model in all_models}

story_flow = {

    'BugzillaBug': {
        'forward_relationship': BugzillaBug.resolved_by_commits.definition['relation_type'],
        'forward_label': DistGitCommit.__label__,
        'backward_relationship': None,
        'backward_label': None
    },
    'DistGitCommit': {
        'forward_relationship': DistGitCommit.koji_builds.definition['relation_type'],
        'forward_label': KojiBuild.__label__,
        'backward_relationship': DistGitCommit.resolved_bugs.definition['relation_type'],
        'backward_label': BugzillaBug.__label__
    },
    'KojiBuild': {
        'forward_relationship': KojiBuild.advisories.definition['relation_type'],
        'forward_label': Advisory.__label__,
        'backward_relationship': KojiBuild.commit.definition['relation_type'],
        'backward_label': DistGitCommit.__label__
    },
    'Advisory': {
        'forward_relationship': Advisory.triggered_freshmaker_event.definition['relation_type'],
        'forward_label': FreshmakerEvent.__label__,
        'backward_relationship': Advisory.attached_builds.definition['relation_type'],
        'backward_label': KojiBuild.__label__
    },
    'FreshmakerEvent': {
        'forward_relationship': (FreshmakerEvent.triggered_container_builds
                                 .definition['relation_type']),
        'forward_label': ContainerBuilds.__label__,
        'backward_relationship': (FreshmakerEvent.triggered_by_advisory
                                  .definition['relation_type']),
        'backward_label': Advisory.__label__
    },
    'ContainerBuilds': {
        'forward_relationship': None,
        'forward_label': None,
        'backward_relationship': (ContainerBuilds.triggered_by_freshmaker_event
                                  .definition['relation_type']),
        'backward_label': FreshmakerEvent.__label__
    }

}


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
