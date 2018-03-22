#! /usr/bin/env python
# SPDX-License-Identifier: GPL-3.0+

import argparse
import logging
import sys
import os
# So we can import the scrapers module
sys.path.insert(1, os.path.abspath(os.path.join(sys.path[0], '..')))

import scrapers  # noqa: E402

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Run a scraper')
parser.add_argument('scraper', type=str, help='The scraper to run')
parser.add_argument('--since', type=str, help='A UTC date formatted in "yyyy-mm-dd" limit results')
parser.add_argument('--teiid-user', type=str, help='The Teiid user')
parser.add_argument('--teiid-password', type=str, help='The Teiid password')
parser.add_argument('--kerberos', action='store_true', help='Use Kerberos for authentication')
args = parser.parse_args()

log.debug('Searching for the "{0}" scraper'.format(args.scraper))
scraper = None
for item in dir(scrapers):
    if item.endswith('Scraper') and item[0:-7].lower() == args.scraper.lower():
        log.debug('Matched "scraper.{0}" to the desired scraper of "{1}"'.format(
            item, args.scraper))
        scraper = getattr(scrapers, item)(args.teiid_user, args.teiid_password, args.kerberos)
        break

if scraper is None:
    error = 'A scraper for "{0}" couldn\'t be found'.format(args.scraper)
    log.error(error)
    raise RuntimeError(error)

scraper.run(since=args.since)
