# SPDX-License-Identifier: GPL-3.0+
# Import all scrapers here so that the scrape script can find them
from scrapers.koji import KojiScraper
from scrapers.distgit import DistGitScraper
from scrapers.bugzilla import BugzillaScraper
from scrapers.errata import ErrataScraper
from scrapers.freshmaker import FreshmakerScraper

# Define the scrapers here in the order that they should be run
all_scrapers = (BugzillaScraper, DistGitScraper, KojiScraper, ErrataScraper, FreshmakerScraper)
