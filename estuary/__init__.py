# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import logging
import pkg_resources


log = logging.getLogger('estuary')

try:
    version = pkg_resources.get_distribution('estuary').version
except pkg_resources.DistributionNotFound:
    version = 'unknown'
