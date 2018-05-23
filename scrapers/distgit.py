# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from multiprocessing.dummy import Pool as ThreadPool
from os import getenv

from builtins import bytes
from bs4 import BeautifulSoup
from requests import ConnectionError

from scrapers.base import BaseScraper
from scrapers.utils import retry_session
from purview.utils.general import timestamp_to_datetime
from purview.models.distgit import DistGitRepo, DistGitBranch, DistGitPush, DistGitCommit
from purview.models.bugzilla import BugzillaBug
from purview.models.user import User
from purview import log


class DistGitScraper(BaseScraper):
    """Scrapes the GitBZ tables in Teiid."""

    cgit_url = getenv('PURVIEW_CGIT_URL', 'http://pkgs.devel.redhat.com/cgit/')
    # The tuple of namespaces to try when determining which namespace this git module belongs
    # to since this information isn't stored in GitBZ yet
    namespaces = ('rpms', 'containers', 'modules', 'tests')

    def run(self, since=None):
        """
        Run the dist-git scraper.

        :param str since: a datetime to start scraping data from
        """
        log.info('Starting initial load of dist-git commits and pushes')
        if since is None:
            dt_since = self.default_since
        else:
            dt_since = timestamp_to_datetime(since)
        results = self.get_distgit_data(dt_since)
        log.info('Successfully fetched {0} results from Teiid'.format(len(results)))
        self.update_neo4j(results)
        log.info('Initial load of dist-git commits and pushes complete!')

    def update_neo4j(self, results):
        """
        Update Neo4j with the dist-git commit and push information from Teiid.

        :param list results: a list of dictionaries
        """
        pool = ThreadPool(8)
        counter = 0
        for result in results:
            if counter % 200 == 0:
                until = counter + 200
                if until > len(results):
                    until = len(results)
                # Because of the joins in the SQL query, we end up with several rows with the same
                # commit hash and we only want to query cgit once per commit
                unique_commits = set([(c['module'], c['sha']) for c in results[counter:until]])
                log.debug('Getting the author and committer email addresses from cgit in parallel '
                          'for results {0} to {1}'.format(counter, until))
                repos_info = {r['commit']: r for r in pool.map(self._get_repo_info, unique_commits)}
                # This is no longer needed so it can be cleared to save RAM
                del unique_commits
            counter += 1
            log.info('Processing commit and push entry {0}/{1}'.format(
                str(counter), str(len(results))))
            repo_info = repos_info[result['sha']]
            if not repo_info.get('namespace'):
                log.info('Skipping nodes creation with commit ID {0} and push ID {1}'.format(
                    result['commit_id'], result['push_id']))
                continue

            log.debug('Creating nodes associated with commit ID {0} and push ID {1}'.format(
                result['commit_id'], result['push_id']))
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
            push = DistGitPush.get_or_create({
                'id_': result['push_id'],
                'push_date': result['push_date'],
                'push_ip': result['push_ip']
            })[0]
            bug = BugzillaBug.get_or_create({'id_': result['bugzilla_id']})[0]

            log.debug('Creating the user nodes associated with commit ID {0} and push ID {1}'
                      .format(result['commit_id'], result['push_id']))
            author = User.create_or_update({
                'username': repo_info['author_username'],
                'email': repo_info['author_email']
            })[0]
            committer = User.create_or_update({
                'username': repo_info['committer_username'],
                'email': repo_info['committer_email']
            })[0]
            pusher = User.get_or_create({
                'username': result['pusher']
            })[0]

            log.debug('Creating the relationships associated with commit ID {0} and push ID {1}'
                      .format(result['commit_id'], result['push_id']))
            repo.contributors.connect(author)
            repo.contributors.connect(committer)
            repo.contributors.connect(pusher)
            repo.commits.connect(commit)
            repo.pushes.connect(push)
            repo.branches.connect(branch)

            branch.contributors.connect(author)
            branch.contributors.connect(committer)
            branch.contributors.connect(pusher)
            branch.commits.connect(commit)
            branch.pushes.connect(push)

            push.conditional_connect(push.pusher, pusher)
            push.commits.connect(commit)

            commit.conditional_connect(commit.author, author)
            commit.conditional_connect(commit.committer, committer)

            if repo_info['parent']:
                parent_commit = DistGitCommit.get_or_create({'hash_': repo_info['parent']})[0]
                commit.conditional_connect(commit.parent, parent_commit)

            if result['bugzilla_type'] == 'related':
                commit.related_bugs.connect(bug)
            elif result['bugzilla_type'] == 'resolves':
                commit.resolved_bugs.connect(bug)
            elif result['bugzilla_type'] == 'reverted':
                commit.reverted_bugs.connect(bug)

    def get_distgit_data(self, since):
        """
        Query Teiid for the dist-git commit, push, and Bugzilla information.

        :param datetime.datetime since: determines when to start the query
        :return: a list of dictionaries
        :rtype: list
        """
        sql = """\
            SELECT c.commit_id, c.author, c.author_date, c.committer, c.commit_date, c.log_message,
                c.sha, bz.bugzilla_id, bz.type as bugzilla_type, p.push_date, p.push_ip, p.module,
                p.ref, p.push_id, p.pusher
            FROM gitbz.git_commits as c
            LEFT JOIN gitbz.git_push_commit_map as map ON c.commit_id = map.commit_id
            LEFT JOIN gitbz.git_pushes as p ON p.push_id = map.push_id
            LEFT JOIN gitbz.redhat_bugzilla_references as bz ON c.commit_id = bz.commit_id
            WHERE c.commit_date > '{0}'
            ORDER BY c.commit_id ASC;
        """.format(since)
        log.info('Getting dist-git commits since {0}'.format(since))
        return self.teiid.query(sql)

    def _get_repo_info(self, repo_and_commit):
        """
        Query cgit for the namespace, parent commit, username and email of the author and committer.

        :param tuple repo_and_commit: contains the repo and commit to query for
        :return: a dictionary with the keys namespace, author_username, author_email,
        committer_username, committer_email, and the commit
        :rtype: dictionary
        """
        repo, commit = repo_and_commit
        log.debug('Attempting to find the cgit URL for the commit "{0}" in repo "{1}"'
                  .format(commit, repo))
        session = retry_session()
        rv = {'commit': commit, 'parent': None}
        cgit_result = None
        for namespace in self.namespaces:
            url = '{0}{1}/{2}/commit/?id={3}'.format(self.cgit_url, namespace, repo, commit)
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
                      .format(commit, repo, ', '.join(self.namespaces)))
            return rv

        log.debug('Found the cgit URL "{0}" for the commit "{1}" in repo "{2}"'.format(
            url, commit, repo))
        rv['namespace'] = namespace

        # Start parsing the cgit content
        soup = BeautifulSoup(cgit_result.text, 'html.parser')
        # Workaround for BS4 in EL7 since `soup.find('th', string=person)` doesn't work in
        # that environment
        th_tags = soup.find_all('th')
        data_found = {'author': False, 'committer': False, 'parent': False}
        for th_tag in th_tags:
            if th_tag.string in ('author', 'committer'):
                data_found[th_tag.string] = True
                username_key = '{0}_username'.format(th_tag.string)
                email_key = '{0}_email'.format(th_tag.string)
                rv[username_key], rv[email_key] = self._parse_username_email_from_cgit(
                    th_tag, commit, namespace, repo)
            elif th_tag.string == 'parent':
                data_found['parent'] = True
                rv['parent'] = th_tag.next_sibling.find('a').string

            # If all the "th" elements we're interested in were parsed, then break from the loop
            # early
            if all(data_found.values()):
                break

        return rv

    @staticmethod
    def _parse_username_email_from_cgit(th_tag, commit, namespace, repo):
        """
        Parse the username and email address from a cgit "th" element of author or committer.

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
