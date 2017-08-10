#!/ust/bin/env python
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import git
import glob
import logging
import os
import pprint
import sys
import yaml


class SetWorkingDir(object):
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        os.chdir(self.new_dir)

    def __exit__(self, *args):
        os.chdir(self.old_dir)


class RepoData(object):
    PUBLIC_ATTRS = ['repo', 'type', 'model', 'team', 'governed']

    def __init__(self, repo, release_type=None, release_model=None,
                 team=None):
        self.repo = repo
        self.type = release_type
        self.model = release_model
        self.team = team
        self.governed = False

        try:
            self._gitRepo = git.Repo(repo)
        except git.exc.NoSuchPathError:
            self._gitRepo = None
            print('repo:%(repo)s is not accessible or is not a git Repo'
                  % (self), file=sys.stderr)

    def __str__(self):
        return self.repo

    def __getitem__(self, key):
        if key in self.PUBLIC_ATTRS:
            return getattr(self, key)
        elif key == 'short_repo':
            return self.repo[10:]
        else:
            raise KeyError()

    def __lt__(self, other):
        return str(self) < str(other)

    def has_branch(self, series):
        if self._gitRepo:
            return 'origin/stable/%s' % series in self._gitRepo.refs
        else:
            return False


def repo_sort_key(repo):
    return '%(type)s:%(team)s:%(repo)s' % (repo)


repos = {}
block_repos = {}
governed_repos = {}
series = 'pike'
base = os.path.join(os.path.expanduser('~'), 'projects', 'openstack')
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)

with SetWorkingDir(base):
    gov = os.path.join('openstack', 'governance', 'reference', 'projects.yaml')
    with open(gov) as f:
        governance = yaml.safe_load(f)

    for team, team_data in governance.items():
        for repo, repo_data in team_data.get('deliverables', {}).items():
            for repo in repo_data.get('repos', []):
                governed_repos[repo] = team

    projects_txt = os.path.join('openstack', 'requirements', 'projects.txt')
    with open(projects_txt) as f:
        data = f.read()
    for repo in data.splitlines():
        repos[repo] = RepoData(repo)

    releases_dir = os.path.join('openstack', 'releases', 'deliverables')
    files = glob.glob(os.path.join(releases_dir, series, '*.yaml'))
    # Some of the data may be in older files?
    # files += glob.glob(os.path.join(releases_dir, 'ocata', '*.yaml'))
    files += glob.glob(os.path.join(releases_dir, '_independent', '*.yaml'))
    for file in files:
        with open(file) as f:
            data = yaml.safe_load(f)
        for deliverable in data.get('releases', {}):
            for project in deliverable.get('projects', {}):
                repo = project.get('repo')
                if repo in repos:
                    repos[repo].model = data.get('release-model', 'independent')
                    repos[repo].team = data.get('team', 'Unknown')
                    repos[repo].type = data.get('type', 'Unknown')

# Remove requirements as well we know it'll look like an error
repos.pop('openstack/requirements')

for repo_name in sorted(repos):
    repo = repos[repo_name]
    if repo_name in governed_repos:
        repo.governed = True
        if repo.team is None:
            repo.team = governed_repos[repo_name]
            logging.debug('Set team name for %(repo)s to %(team)s' % (repo))

    # Yck fixups
    if (repo_name.startswith('openstack/openstack-ansible') or
            repo.team == 'OpenStackAnsible'):
        logging.debug('Fixing up OpenStackAnsible repo %s' % repo_name)
        repo.team = 'OpenStackAnsible'
        repo.model = 'cycle-trailing'
        repo.type = 'other'
    if repo_name.startswith('openstack/kolla') or repo.team == 'kolla':
        logging.debug('Fixing up Kolla repo %s' % repo_name)
        repo.team = 'kolla'
        repo.model = 'cycle-trailing'
        repo.type = 'other'
    if repo_name.startswith('openstack/tripleo') or repo.team == 'tripleo':
        logging.debug('Fixing up TripleO repo %s' % repo_name)
        repo.team = 'tripleo'
        repo.model = 'cycle-trailing'
        repo.type = 'other'
    if repo_name == 'openstack/octavia-tempest-plugin':
        logging.debug('Fixing up Octavia repo %s' % repo_name)
        repo.team = 'octavia'
        repo.model = 'independent'
        repo.type = 'other'

    # The independent release_model isn't tied to a series so just ignore them
    if repo.model == 'independent':
        logging.debug('Ignoring %(model)s repo %(repo)s' % (repo))
        repos.pop(repo_name)
        continue
    # A repo is ok if:
    # - it already have a series branch
    # - it is a cycle-with-milestones, as requirements wont branch until after
    #   it has a series branch
    if repo.has_branch(series) or repo.model == 'cycle-with-milestones':
        logging.debug('All Good %(repo)s' % (repo))
        repos.pop(repo_name)
        continue
    # A repo needs to be blocked if:
    # - it is branchless (tempest-plugin) or
    # - it is a cycle-trailing, as we'll work with those teams to manually
    #   block g-r bot updates.
    if (repo.model == 'cycle-trailing' or 'tempest-plugin' in repo_name):
        logging.debug('Adding %(repo)s to block list' % (repo))
        block_repos[repo_name] = repos.pop(repo_name)
        continue

print(('Projects without team or release model could not be found in '
       'openstack/releases for %s' % series))
release_type = None
affected_teams = set()
for repo in sorted(repos.values(), key=repo_sort_key):
    if release_type != repo.type:
        release_type = repo.type
        print('\nRepos with type: %s' % release_type)
    if repo.team is None:
        print('%(repo)s' % (repo))
    else:
        print('%(short_repo)-50s %(team)-20s' % (repo))
    repos.pop(repo.repo)
    affected_teams.add(repo.team)

print('[%s] %s' % (']['.join(x for x in sorted(affected_teams) if x),
                   'Help needed'))
print('')
affected_teams = set()
for repo in sorted(block_repos.values(), key=repo_sort_key):
    affected_teams.add(repo.team)
    print('%(short_repo)-50s %(team)-20s' % (repo))
print('[%s] %s' % (']['.join(x for x in sorted(affected_teams) if x),
                   'Warning'))

if repos != {}:
    logging.error('Repos list is not empty')
    for repo in sorted(repos.values(), key=repo_sort_key):
        logging.error(pprint.pformat(repo.__dict__))
