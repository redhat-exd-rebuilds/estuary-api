#! /usr/bin/env python
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import argparse
import logging
import sys
import os
# So we can import the scrapers module
sys.path.insert(1, os.path.abspath(os.path.join(sys.path[0], '..')))

from scrapers import all_scrapers  # noqa: E402

logging.basicConfig(format='[%(filename)s:%(lineno)s:%(funcName)s] %(message)s')
log = logging.getLogger('purview')
log.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description='Run a scraper')
parser.add_argument('scraper', type=str, help='The scraper to run. To run them all, use "all".')
parser.add_argument('--since', type=str,
                    help='Process results starting from a UTC date formatted in "yyyy-mm-dd"')
parser.add_argument('--teiid-user', type=str, help='The Teiid user')
parser.add_argument('--teiid-password', type=str, help='The Teiid password')
parser.add_argument('--neo4j-user', type=str, default='neo4j', help='The Neo4j user')
parser.add_argument('--neo4j-password', type=str, default='neo4j', help='The Neo4j password')
parser.add_argument('--neo4j-server', type=str, default='localhost',
                    help='The FQDN to the Neo4j server')
parser.add_argument('--kerberos', action='store_true', help='Use Kerberos for authentication')
args = parser.parse_args()

scraper_classes = tuple()
if args.scraper.lower() == 'all':
    log.debug('Running all the scrapers in order')
    scraper_classes = all_scrapers
else:
    log.debug('Searching for the "{0}" scraper'.format(args.scraper))
    for item in all_scrapers:
        if item.__name__[0:-7].lower() == args.scraper.lower():
            log.debug('Matched "scraper.{0}" to the desired scraper of "{1}"'.format(
                item.__name__, args.scraper))
            scraper_classes = tuple([item])
            break

if not scraper_classes:
    error = 'A scraper for "{0}" couldn\'t be found'.format(args.scraper)
    log.error(error)
    raise RuntimeError(error)

for scraper_class in scraper_classes:
    scraper = scraper_class(
        args.teiid_user, args.teiid_password, args.kerberos, args.neo4j_user, args.neo4j_password,
        args.neo4j_server)
    scraper.run(since=args.since)
