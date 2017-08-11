#!/usr/bin/env python
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

""" The purpose of this tool is to append a templated string to a commit mesage
    in the scenario that the requirements repo has branched but the project
    repo has not.  This could indicated that the proposed chnages are destined
    for the next release of OpenStack and shoudl be reviewed carefully.
"""

from __future__ import print_function

import argparse
import git
import sys

# NOTE(tonyb): It would be very nice if we could get this from somewhere.
#              The only place I know of is openstack/releases, but I'm not
#              sure that's something we can use here.
# In the meantime a review to change this should be the first thing to merge
# post branching
RELEASE_SERIES = 'pike'
SERIES_BRANCH = 'origin/stable/%s' % RELEASE_SERIES
COMMIT_WARNING = """%(initial_commit_message)s

WARNING! This proposal was generated from the requirements master branch but
it seems %(project)s does not yet contain a "%(short_branch)s" branch.

Please review carefully"""


# WARNING!  This needs to exist on all branches before we can us it in the
# gate
def main(argv=None):
    parser = argparse.ArgumentParser(description='Generate commit message')
    parser.add_argument('--message', dest='message', required=True)
    parser.add_argument('--git-base', dest='git_base', required=True)
    parser.add_argument('--project', dest='project', required=True)
    parser.add_argument('--branch', dest='branch', required=True)
    args = parser.parse_args(argv or sys.argv)

    if args.branch == 'origin/master':
        requirements_repo = git.Repo(args.git_base)
        project_repo = git.Repo('.')

        if (SERIES_BRANCH in requirements_repo.refs and
                SERIES_BRANCH not in project_repo.refs):
            print(COMMIT_WARNING %
                  ({'initial_commit_message': args.message,
                    'project': args.project,
                    'short_branch': SERIES_BRANCH[7:]
                    }))
            return 0
    print(args.message)
    return 0
