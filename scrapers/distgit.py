# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
import re
from multiprocessing.dummy import Pool as ThreadPool

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
    cgit_url = 'http://pkgs.devel.redhat.com/cgit/'
    # The tuple of namespaces to try when determining which namespace this git module belongs
    # to since this information isn't stored in GitBZ yet
    namespaces = ('rpms', 'containers', 'modules', 'tests')

    def run(self, since=None):
        """
        Main function that runs the dist-git scraper
        :param since: a string representing a datetime to start scraping data from
        :return: None
        """
        log.info('Starting initial load of dist-git commits and pushes')
        if since is None:
            dt_since = self.default_since
        else:
            dt_since = timestamp_to_datetime(since)
        results = self.get_distgit_data(dt_since)
        log.info('Successfully fetched {0} results from TEIID'.format(len(results)))
        self.update_neo4j(results)
        log.info('Initial load of dist-git commits and pushes complete!')

    def update_neo4j(self, results):
        """
        Update Neo4j with the dist-git commit and push information from TEIID
        :param results: a list of dictionaries
        :return: None
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
            branch = DistGitBranch.get_or_create(
                {'name': branch_name}, relationships=repo.branches)[0]
            commit = DistGitCommit.get_or_create({
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
            author.distgit_authored_commits.connect(commit)
            author.distgit_branches.connect(branch)
            author.distgit_repos.connect(repo)

            committer.distgit_committed_commits.connect(commit)
            committer.distgit_branches.connect(branch)
            committer.distgit_repos.connect(repo)

            pusher.distgit_pushes.connect(push)
            pusher.distgit_branches.connect(branch)
            pusher.distgit_repos.connect(repo)

            repo.contributors.connect(author)
            repo.contributors.connect(committer)
            repo.contributors.connect(pusher)
            repo.commits.connect(commit)
            repo.pushes.connect(push)
            repo.branches.connect(branch)

            branch.commits.connect(commit)
            branch.pushes.connect(push)

            push.owners.connect(pusher)
            push.pushers.connect(pusher)
            push.commits.connect(commit)
            push.branches.connect(branch)
            push.repos.connect(repo)

            commit.owners.connect(author)
            commit.authors.connect(author)
            commit.committers.connect(committer)
            commit.pushes.connect(push)
            commit.branches.connect(branch)
            commit.repos.connect(repo)

            if result['bugzilla_type'] == 'related':
                commit.related_bugs.connect(bug)
                bug.related_by_commits.connect(commit)
            elif result['bugzilla_type'] == 'resolves':
                commit.resolved_bugs.connect(bug)
                bug.resolved_by_commits.connect(commit)
            elif result['bugzilla_type'] == 'reverted':
                commit.reverted_bugs.connect(bug)
                bug.reverted_by_commits.connect(commit)

    def get_distgit_data(self, since):
        """
        Query TEIID for the dist-git commit, push, and Bugzilla information
        :param since: a datetime object that determines when to start query
        :return: a list of dictionaries
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
        Query cgit to find the namespace and the username and email address of the author and
        committer
        :param repo_and_commit: a tuple containing the repo and commit to query for
        :return: a dictionary with the keys namespace, author_username, author_email,
        committer_username, committer_email, and the commit
        """
        repo, commit = repo_and_commit
        log.debug('Attempting to find the cgit URL for the commit "{0}" in repo "{1}"'
                  .format(commit, repo))
        session = retry_session()
        rv = {'commit': commit}
        cgit_result = None
        for namespace in self.namespaces:
            url = '{0}{1}/{2}/commit/?id={3}'.format(self.cgit_url, namespace, repo, commit)
            log.debug('Trying the URL "{0}"'.format(url))
            try:
                cgit_result = session.get(url, timeout=15)
            except ConnectionError:
                log.error('The connection to "{0}" failed'.format(url))
                continue

            # If we get a 200 status code, we assume the page has the data we need
            if cgit_result.status_code == 200:
                break

        if not cgit_result or cgit_result.status_code != 200:
            log.error('Couldn\'t find the commit "{0}" for the repo "{1}" in the namespaces: {2}'
                      .format(commit, repo, ', '.join(self.namespaces)))
            return rv

        log.debug('Found the cgit URL "{0}" for the commit "{1}" in repo "{2}"'.format(
            url, commit, repo))
        soup = BeautifulSoup(cgit_result.text, 'html.parser')
        rv['namespace'] = namespace
        for person in ('author', 'committer'):
            # Set some defaults in the event the cgit entry is malformed
            rv['{0}_username'.format(person)] = None
            rv['{0}_email'.format(person)] = None
            # Workaround for BS4 in EL7 since `soup.find('th', string=person)` doesn't work in
            # that environment
            th_tags = soup.find_all('th')
            td_text = None
            for th_tag in th_tags:
                if th_tag.string == 'author':
                    td_text = th_tag.next_sibling.string
            error_msg = 'Couldn\'t find the {0} for the commit "{1}" on repo "{2}/{3}"'.format(
                person, commit, namespace, repo)
            if td_text is None:
                log.error(error_msg)
                continue

            match = re.match(
                r'^.+<(?P<email>(?P<username>.+)@(?P<domain>.+))>$', td_text)
            if not match:
                log.error(error_msg)
                continue

            match_dict = match.groupdict()
            if match_dict['domain'] == 'redhat.com':
                rv['{0}_username'.format(person)] = match_dict['username']
            else:
                # If the email isn't a Red Hat email address, then use the whole email address
                # as the username. This should only happen with erroneous git configurations.
                rv['{0}_username'.format(person)] = match_dict['email']
            rv['{0}_email'.format(person)] = match_dict['email']

        return rv
