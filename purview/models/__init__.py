# SPDX-License-Identifier: GPL-3.0+

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
