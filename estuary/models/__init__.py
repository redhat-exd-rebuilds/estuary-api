# SPDX-License-Identifier: GPL-3.0+

from estuary.models.koji import ContainerKojiBuild, KojiBuild, KojiTask, KojiTag
from estuary.models.bugzilla import BugzillaBug
from estuary.models.distgit import DistGitRepo, DistGitPush, DistGitBranch, DistGitCommit
from estuary.models.errata import Advisory, AdvisoryState
from estuary.models.freshmaker import FreshmakerEvent
from estuary.models.user import User

all_models = (Advisory, AdvisoryState, BugzillaBug, ContainerKojiBuild, DistGitBranch,
              DistGitCommit, DistGitPush, DistGitRepo, FreshmakerEvent, KojiBuild,
              KojiTag, KojiTask, User)
names_to_model = {model.__label__: model for model in all_models}
story_flow_list = ['BugzillaBug', 'DistGitCommit', 'KojiBuild',
                   'Advisory', 'FreshmakerEvent', 'ContainerKojiBuild']
