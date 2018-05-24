# SPDX-License-Identifier: GPL-3.0+

from purview.models.koji import KojiBuild, KojiTask, KojiTag
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitRepo, DistGitPush, DistGitBranch, DistGitCommit
from purview.models.errata import Advisory, AdvisoryState
from purview.models.freshmaker import FreshmakerEvent
from purview.models.user import User

all_models = (Advisory, AdvisoryState, BugzillaBug, DistGitBranch,
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
        'forward_relationship': None,
        'forward_label': None,
        'backward_relationship': '{0}>'.format(FreshmakerEvent.triggered_by_advisory
                                               .definition['relation_type']),
        'backward_label': Advisory.__label__
    }
}
