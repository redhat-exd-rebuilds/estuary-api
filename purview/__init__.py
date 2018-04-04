# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import logging
import pkg_resources


log = logging.getLogger('purview')

try:
    version = pkg_resources.get_distribution('purview').version
except pkg_resources.DistributionNotFound:
    version = 'unknown'
