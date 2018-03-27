# SPDX-License-Identifier: GPL-3.0+
# Import all scrapers here so that the scrape script can find them
from scrapers.koji import KojiScraper  # noqa: F401
from scrapers.distgit import DistGitScraper  # noqa: F401
