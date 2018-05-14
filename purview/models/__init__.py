# SPDX-License-Identifier: GPL-3.0+

from neomodel import RelationshipManager
from neomodel.relationship_manager import check_source, _rel_helper

from purview.models.koji import KojiBuild, KojiTask, KojiTag
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitRepo, DistGitPush, DistGitBranch, DistGitCommit
from purview.models.errata import Advisory, AdvisoryState
from purview.models.freshmaker import FreshmakerEvent, ContainerBuild
from purview.models.user import User

all_models = (Advisory, AdvisoryState, BugzillaBug, ContainerBuild, DistGitBranch,
              DistGitCommit, DistGitPush, DistGitRepo, FreshmakerEvent, KojiBuild,
              KojiTag, KojiTask, User)
names_to_model = {model.__label__: model for model in all_models}

story_flow = {

    'BugzillaBug': {
        'uid_name': BugzillaBug.id_.db_property or BugzillaBug.id.name,
        'forward_relationship': '{0}<'.format(
            BugzillaBug.resolved_by_commits.definition['relation_type']),
        'forward_label': DistGitCommit.__label__,
        'backward_relationship': None,
        'backward_label': None
    },
    'DistGitCommit': {
        'uid_name': DistGitCommit.hash_.db_property or DistGitCommit.hash.name,
        'forward_relationship': '{0}<'.format(
            DistGitCommit.koji_builds.definition['relation_type']),
        'forward_label': KojiBuild.__label__,
        'backward_relationship': '{0}>'.format(
            DistGitCommit.resolved_bugs.definition['relation_type']),
        'backward_label': BugzillaBug.__label__
    },
    'KojiBuild': {
        'uid_name': KojiBuild.id_.db_property or KojiBuild.id.name,
        'forward_relationship': '{0}<'.format(KojiBuild.advisories.definition['relation_type']),
        'forward_label': Advisory.__label__,
        'backward_relationship': '{0}>'.format(KojiBuild.commit.definition['relation_type']),
        'backward_label': DistGitCommit.__label__
    },
    'Advisory': {
        'uid_name': Advisory.id_.db_property or Advisory.id.name,
        'forward_relationship': '{0}<'.format(
            Advisory.triggered_freshmaker_event.definition['relation_type']),
        'forward_label': FreshmakerEvent.__label__,
        'backward_relationship': '{0}>'.format(
            Advisory.attached_builds.definition['relation_type']),
        'backward_label': KojiBuild.__label__
    },
    'FreshmakerEvent': {
        'uid_name': FreshmakerEvent.id_.db_property or FreshmakerEvent.id.name,
        'forward_relationship': '{0}>'.format(FreshmakerEvent.triggered_container_builds
                                              .definition['relation_type']),
        'forward_label': ContainerBuild.__label__,
        'backward_relationship': '{0}>'.format(FreshmakerEvent.triggered_by_advisory
                                               .definition['relation_type']),
        'backward_label': Advisory.__label__
    },
    'ContainerBuild': {
        'uid_name': ContainerBuild.id_.db_property or ContainerBuild.id.name,
        'forward_relationship': None,
        'forward_label': None,
        'backward_relationship': '{0}<'.format(ContainerBuild.triggered_by_freshmaker_event
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
