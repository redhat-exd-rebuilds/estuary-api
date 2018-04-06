# SPDX-License-Identifier: GPL-3.0+

from purview.models.koji import KojiBuild, KojiTask, KojiTag
from purview.models.bugzilla import BugzillaBug
from purview.models.distgit import DistGitRepo, DistGitPush, DistGitBranch, DistGitCommit
from purview.models.errata import Advisory, AdvisoryState
from purview.models.freshmaker import FreshmakerEvent, ContainerBuilds
from purview.models.user import User

all_models = {Advisory, AdvisoryState, BugzillaBug, ContainerBuilds, DistGitBranch,
              DistGitCommit, DistGitPush, DistGitRepo, FreshmakerEvent, KojiBuild,
              KojiTag, KojiTask, User}
