# SPDX-License-Identifier: GPL-3.0+
# Import all scrapers here so that the scrape script can find them
from scrapers.bugzilla import BugzillaScraper
from scrapers.distgit import DistGitScraper
from scrapers.errata import ErrataScraper
from scrapers.freshmaker import FreshmakerScraper
from scrapers.koji import KojiScraper

# Define the scrapers here in the order that they should be run
all_scrapers = (BugzillaScraper, DistGitScraper, KojiScraper, ErrataScraper, FreshmakerScraper)
