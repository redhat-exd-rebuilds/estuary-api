# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from os import getenv
from itertools import islice
from functools import partial

from builtins import bytes
from bs4 import BeautifulSoup
from requests import ConnectionError
from neomodel import config as neomodel_config

from scrapers.base import BaseScraper
from scrapers.utils import retry_session
from estuary.utils.general import timestamp_to_date
from estuary.models.distgit import DistGitRepo, DistGitBranch, DistGitCommit
from estuary.models.bugzilla import BugzillaBug
from estuary.models.user import User
from estuary import log


class DistGitScraper(BaseScraper):
    """Scrapes the GitBZ tables in Teiid."""

    def run(self, since=None, until=None):
        """
        Run the dist-git scraper.

        :param str since: a datetime to start scraping data from
        :param str until: a datetime to scrape data until
        """
        log.info('Starting initial load of dist-git commits')
        if since is None:
            start_date = self.default_since
        else:
            start_date = timestamp_to_date(since)

        if until is None:
            end_date = self.default_until
        else:
            end_date = timestamp_to_date(until)
        results = self.get_distgit_data(start_date, end_date)
        log.info('Successfully fetched {0} results from Teiid'.format(len(results)))
        # Upload the results to Neo4j
        _update_neo4j_partial = partial(
            self._update_neo4j, neomodel_config.DATABASE_URL, len(results))
        # Create a multi-processing pool to process chunks of results
        pool = Pool(2)
        # Overwrite results with the formatted results so we don't have to store both in RAM
        results = list(self._get_result_chunks(results))
        pool.map(_update_neo4j_partial, results)
        log.info('Initial load of dist-git commits complete!')

    @staticmethod
    def _get_result_chunks(results):
        """
        Yield a tuple with a counter and chunk of results.

        :param list results: a list of dictionaries representing results from Teiid to chunk up
        :return: generator of a tuple with a counter and chunk of results
        :rtype: generator
        """
        list_iterator = iter(results)
        chunk_size = 600
        count = 0
        while True:
            chunk = list(islice(list_iterator, chunk_size))
            if chunk:
                yield (count, chunk)
            else:
                break
            count += chunk_size

    @staticmethod
    def _update_neo4j(neo4j_url, total_results, counter_and_results):
        """
        Update Neo4j results via mapping with multiprocessing.

        :param str neo4j_url: database url for Neo4j
        :param int total_results: the total number of results that will be processed. This is used
        for a logging statement about progress.
        :param tuple counter_and_results: a tuple where the first index is the current counter and
        the second index is a list of dictionaries representing results from Teiid
        """
        previous_total = counter_and_results[0]
        results = counter_and_results[1]
        # Since _update_neo4j will be run in a separate process, we must configure the database
        # URL every time the method is run.
        neomodel_config.DATABASE_URL = neo4j_url
        # Create a thread pool with 4 threads to speed up queries to cgit
        pool = ThreadPool(4)
        counter = 0
        for result in results:
            if counter % 200 == 0:
                until = counter + 200
                if until > len(results):
                    until = len(results)
                # Because of the joins in the SQL query, we end up with several rows with the same
                # commit hash and we only want to query cgit once per commit
                unique_commits = set([(c['module'], c['sha']) for c in results[counter:until]])
                log.debug('Getting the author email addresses from cgit in parallel '
                          'for results {0} to {1}'.format(counter, until))
                repos_info = {r['commit']: r for r in pool.map(
                    DistGitScraper._get_repo_info, unique_commits)}
                # This is no longer needed so it can be cleared to save RAM
                del unique_commits
            counter += 1
            log.info('Processing commit entry {0}/{1}'.format(
                previous_total + counter, total_results))
            repo_info = repos_info[result['sha']]
            if not repo_info.get('namespace'):
                log.info('Skipping nodes creation with commit ID {0}'.format(
                    result['commit_id']))
                continue

            log.debug('Creating nodes associated with commit ID {0}'.format(
                result['commit_id']))
            repo = DistGitRepo.get_or_create({
                'namespace': repo_info['namespace'],
                'name': result['module']
            })[0]
            branch_name = result['ref'].rsplit('/', 1)[1]
            branch = DistGitBranch.get_or_create({
                'name': branch_name,
                'repo_namespace': repo_info['namespace'],
                'repo_name': result['module']
            })[0]
            commit = DistGitCommit.create_or_update({
                'author_date': result['author_date'],
                'commit_date': result['commit_date'],
                'hash_': result['sha'],
                # In case we get unicode characters in Python 2
                'log_message': bytes(result['log_message'], 'utf-8').decode()
            })[0]
            bug = BugzillaBug.get_or_create({'id_': result['bugzilla_id']})[0]

            log.debug('Creating the user nodes associated with commit ID {0}'
                      .format(result['commit_id']))
            author = User.create_or_update({
                'username': repo_info['author_username'],
                'email': repo_info['author_email']
            })[0]

            log.debug('Creating the relationships associated with commit ID {0}'
                      .format(result['commit_id']))
            repo.contributors.connect(author)
            repo.commits.connect(commit)
            repo.branches.connect(branch)

            branch.contributors.connect(author)
            branch.commits.connect(commit)

            commit.conditional_connect(commit.author, author)

            if repo_info['parent']:
                parent_commit = DistGitCommit.get_or_create({'hash_': repo_info['parent']})[0]
                commit.conditional_connect(commit.parent, parent_commit)

            if result['bugzilla_type'] == 'related':
                commit.related_bugs.connect(bug)
            elif result['bugzilla_type'] == 'resolves':
                commit.resolved_bugs.connect(bug)
            elif result['bugzilla_type'] == 'reverted':
                commit.reverted_bugs.connect(bug)
            # This is no longer needed so it can be cleared to save RAM
            del repo_info

    def get_distgit_data(self, since, until):
        """
        Query Teiid for the dist-git commit and Bugzilla information.

        :param datetime.datetime since: determines when to start the query
        :param datetime.datetime until: determines until when to scrape data
        :return: a list of dictionaries
        :rtype: list
        """
        sql = """\
            SELECT c.commit_id, c.author, c.author_date, c.commit_date, c.log_message,
                c.sha, bz.bugzilla_id, bz.type as bugzilla_type, p.module, p.ref
            FROM gitbz.git_commits as c
            LEFT JOIN gitbz.git_push_commit_map as map ON c.commit_id = map.commit_id
            LEFT JOIN gitbz.git_pushes as p ON p.push_id = map.push_id
            LEFT JOIN gitbz.redhat_bugzilla_references as bz ON c.commit_id = bz.commit_id
            WHERE c.commit_date >= '{0}' AND c.commit_date <= '{1}'
            ORDER BY c.commit_date DESC;
        """.format(since, until)
        log.info('Getting dist-git commits since {0} until {1}'.format(since, until))
        return self.teiid.query(sql)

    @staticmethod
    def _get_repo_info(repo_and_commit):
        """
        Query cgit for the namespace, parent commit, username and email of the author.

        :param tuple repo_and_commit: contains the repo and commit to query for
        :return: a JSON string of a dictionary with the keys namespace, author_username,
        author_email, and the commit
        :rtype: str
        """
        repo, commit = repo_and_commit
        log.debug('Attempting to find the cgit URL for the commit "{0}" in repo "{1}"'
                  .format(commit, repo))
        session = retry_session()
        rv = {'commit': commit, 'parent': None}
        cgit_result = None
        # The tuple of namespaces to try when determining which namespace this git module belongs
        # to since this information isn't stored in GitBZ yet
        namespaces = ('rpms', 'containers', 'modules', 'tests')
        cgit_url = getenv('ESTUARY_CGIT_URL', 'http://pkgs.devel.redhat.com/cgit/')
        for namespace in namespaces:
            url = '{0}{1}/{2}/commit/?id={3}'.format(cgit_url, namespace, repo, commit)
            log.debug('Trying the URL "{0}"'.format(url))
            try:
                cgit_result = session.get(url, timeout=15)
            except ConnectionError:
                log.error('The connection to "{0}" failed'.format(url))
                continue

            if cgit_result.status_code == 200:
                # If the repo is empty, cgit oddly returns a 200 status code, so let's correct the
                # status code so that the remainder of the code knows it's a bad request
                if 'Repository seems to be empty' in cgit_result.text:
                    cgit_result.status_code = 404
                else:
                    # If the repo is populated and a 200 status code is returned, then we can
                    # assume we found the correct repo
                    break

        if not cgit_result or cgit_result.status_code != 200:
            log.error('Couldn\'t find the commit "{0}" for the repo "{1}" in the namespaces: {2}'
                      .format(commit, repo, ', '.join(namespaces)))
            return rv

        log.debug('Found the cgit URL "{0}" for the commit "{1}" in repo "{2}"'.format(
            url, commit, repo))
        rv['namespace'] = namespace

        # Start parsing the cgit content
        soup = BeautifulSoup(cgit_result.text, 'html.parser')
        # Workaround for BS4 in EL7 since `soup.find('th', string=person)` doesn't work in
        # that environment
        th_tags = soup.find_all('th')
        data_found = {'author': False, 'parent': False}
        for th_tag in th_tags:
            if th_tag.string in ('author'):
                data_found[th_tag.string] = True
                username_key = '{0}_username'.format(th_tag.string)
                email_key = '{0}_email'.format(th_tag.string)
                rv[username_key], rv[email_key] = DistGitScraper._parse_username_email_from_cgit(
                    th_tag, commit, namespace, repo)
            elif th_tag.string == 'parent':
                data_found['parent'] = True
                rv['parent'] = th_tag.next_sibling.find('a').string

            # If all the "th" elements we're interested in were parsed, then break from the loop
            # early
            if all(data_found.values()):
                break

        soup.decompose()
        return rv

    @staticmethod
    def _parse_username_email_from_cgit(th_tag, commit, namespace, repo):
        """
        Parse the username and email address from a cgit "th" element of author.

        :param th_tag: a BeautifulSoup4 element object
        :param str commit: the commit being processed
        :param str namespace: the namespace of the repo being processed
        :param str repo: the repo being processed
        :return: a tuple of (username, email)
        :rtype: tuple
        """
        person_text = th_tag.next_sibling.string
        # Set some defaults in the event the cgit entry is malformed
        username = None
        email = None

        if person_text:
            match = re.match(
                r'^.+<(?P<email>(?P<username>.+)@(?P<domain>.+))>$', person_text)
            if match:
                match_dict = match.groupdict()
                if match_dict['domain'].lower() == 'redhat.com':
                    username = match_dict['username'].lower()
                else:
                    # If the email isn't a Red Hat email address, then use the whole email address
                    # as the username. This should only happen with erroneous git configurations.
                    username = match_dict['email'].lower()
                email = match_dict['email'].lower()

        if username is None or email is None:
            log.error('Couldn\'t find the {0} for the commit "{1}" on repo "{2}/{3}"'.format(
                      th_tag.string, commit, namespace, repo))

        return username, email
