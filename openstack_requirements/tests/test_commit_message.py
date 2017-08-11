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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import copy
import mock
import testtools

from openstack_requirements.cmds import gate_commit_message
from openstack_requirements.tests import common

gate_commit_message.RELEASE_SERIES = 'SERIES'
gate_commit_message.SERIES_BRANCH = 'origin/stable/SERIES'


class FakeGitRepo(object):
    def __init__(self, refs):
        self.refs = copy.copy(refs)


class TestGateCommitMessageMaster(testtools.TestCase):
    """Running on master branch so test:

        reqs      project   Running   Result
        [m]       [m]         m       OK      # Mid cycle the norm
        [m]       [m, s]      m       OK      # freeze period
        [m, s]    [m]         m       WARN    # Cycle-trailing!
        [m, s]    [m, s]      m       OK      # Mid cycle the norm
    """
    def setUp(self):
        super(TestGateCommitMessageMaster, self).setUp()
        self.out = self.useFixture(common.OutputStreamCapture())
        self.cli_args = ['--message', 'FOO', '--git-base', 'UNUSED',
                         '--project', 'openstack/awesome',
                         '--branch', 'origin/master']

    @mock.patch('git.Repo',
                side_effect=[FakeGitRepo(['origin/master']),
                             FakeGitRepo(['origin/master'])])
    def test_only_master_branches(self, mock_repo):
        gate_commit_message.main(self.cli_args)
        self.assertTrue(mock_repo.called)
        self.assertEqual('FOO', self.out.stdout)

    @mock.patch('git.Repo',
                side_effect=[FakeGitRepo(['origin/master',
                                          'origin/stable/SERIES']),
                             FakeGitRepo(['origin/master',
                                          'origin/stable/SERIES'])])
    def test_both_repos_branched(self, mock_repo):
        gate_commit_message.main(self.cli_args)
        self.assertTrue(mock_repo.called)
        self.assertEqual('FOO', self.out.stdout)

    @mock.patch('git.Repo',
                side_effect=[FakeGitRepo(['origin/master',
                                          'origin/stable/SERIES']),
                             FakeGitRepo(['origin/master'])])
    def test_warning_reqs_branched_but_not_project(self, mock_repo):
        gate_commit_message.main(self.cli_args)
        self.assertTrue(mock_repo.called)
        self.assertTrue('SERIES' in self.out.stdout)

    @mock.patch('git.Repo',
                side_effect=[FakeGitRepo(['origin/master']),
                             FakeGitRepo(['origin/master',
                                          'origin/stable/SERIES'])])
    def test_project_branched_but_not_reqs(self, mock_repo):
        gate_commit_message.main(self.cli_args)
        self.assertTrue(mock_repo.called)
        self.assertEqual('FOO', self.out.stdout)


class TestGateCommitMessageStable(testtools.TestCase):
    """Anything running on a stable branch is OK but test

        reqs      project   Running   Result
        [m, s]    [m, s]      s       OK      # Mid cycle the norm
      This scenario isn't tested as it's caught in the gate but shoudl be okay
        [m, s]    [m]         s       OK      # project doesn't have a s branch
    """
    def setUp(self):
        super(TestGateCommitMessageStable, self).setUp()
        self.out = self.useFixture(common.OutputStreamCapture())
        self.cli_args = ['--message', 'FOO', '--git-base', 'UNUSED',
                         '--project', 'openstack/awesome',
                         '--branch', 'origin/stable/SERIES']

    @mock.patch('git.Repo')
    def test_running_on_stable_branch(self, mock_repo):
        gate_commit_message.main(self.cli_args)
        self.assertFalse(mock_repo.called)
        self.assertEqual('FOO', self.out.stdout)
