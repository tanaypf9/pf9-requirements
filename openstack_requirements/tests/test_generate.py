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

import sys

import fixtures
import testtools
from testtools import matchers

from openstack_requirements.cmds import generate


class TestFreeze(testtools.TestCase):

    def test_freeze_smoke(self):
        # Assume the default python3 runtime is running a version of python
        # that includes the venv module.
        req = self.useFixture(fixtures.TempDir()).path + '/r.txt'
        with open(req, 'wt') as output:
            output.write('fixtures==1.2.0')
        frozen = generate._freeze(req, '/usr/bin/python3')
        verinfo = sys.version_info
        expected_version = '{}.{}'.format(verinfo.major, verinfo.minor)
        self.expectThat(frozen, matchers.HasLength(2))
        self.expectThat(frozen[0], matchers.Equals(expected_version))
        # There are multiple items in the dependency tree of fixtures.
        # Since this is a smoke test, just ensure fixtures is there.
        self.expectThat(frozen[1], matchers.Contains(('fixtures', '1.2.0')))


class TestParse(testtools.TestCase):

    def test_parse(self):
        text = "linecache2==1.0.0\nargparse==1.2\n\n# fred\n"
        parsed = generate._parse_freeze(text)
        self.assertEqual(
            [('linecache2', '1.0.0'), ('argparse', '1.2')], parsed)

    def test_editable_banned(self):
        text = "-e git:..."
        self.assertRaises(Exception, generate._parse_freeze, text)  # noqa


class TestCombine(testtools.TestCase):

    def test_same_items(self):
        fixtures = [('fixtures', '1.2.0')]
        freeze_27 = ('2.7', fixtures)
        freeze_34 = ('3.4', fixtures)
        self.assertEqual(
            ['fixtures===1.2.0\n'],
            list(generate._combine_freezes([freeze_27, freeze_34])))

    def test_distinct_items(self):
        freeze_27 = ('2.7', [('fixtures', '1.2.0')])
        freeze_34 = ('3.4', [('fixtures', '1.2.0'), ('enum', '1.5.0')])
        self.assertEqual(
            ["enum===1.5.0;python_version=='3.4'\n", 'fixtures===1.2.0\n'],
            list(generate._combine_freezes([freeze_27, freeze_34])))

    def test_different_versions(self):
        freeze_27 = ('2.7', [('fixtures', '1.2.0')])
        freeze_34 = ('3.4', [('fixtures', '1.5.0')])
        self.assertEqual(
            ["fixtures===1.2.0;python_version=='2.7'\n",
             "fixtures===1.5.0;python_version=='3.4'\n"],
            list(generate._combine_freezes([freeze_27, freeze_34])))

    def test_duplicate_pythons(self):
        with testtools.ExpectedException(Exception):
            list(generate._combine_freezes([('2.7', []), ('2.7', [])]))

    def test_blacklist(self):
        blacklist = ['Fixtures']
        freeze_27 = ('2.7', [('fixtures', '1.2.0')])
        freeze_34 = ('3.4', [('fixtures', '1.2.0'), ('enum', '1.5.0')])
        self.assertEqual(
            ["enum===1.5.0;python_version=='3.4'\n"],
            list(generate._combine_freezes(
                [freeze_27, freeze_34], blacklist=blacklist)))

    def test_blacklist_with_safe_name(self):
        blacklist = ['flake8_docstrings']
        freeze_27 = ('2.7', [('flake8-docstrings', '0.2.1.post1'),
                             ('enum', '1.5.0')])
        self.assertEqual(
            ['enum===1.5.0\n'],
            list(generate._combine_freezes(
                [freeze_27], blacklist=blacklist)))


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestClone(testtools.TestCase):

    def test_py34_clone_py35(self):
        # Simulate an environment where we have python 3.4 data and need to
        # clone that to python 3.5
        options = Namespace(version_map={'3.4': set(['3.5']),
                                         '3.5': set(['3.4'])})
        freeze_27 = ('2.7', [('dnspython', '1.15.0')])
        freeze_34 = ('3.4', [('dnspython3', '1.12.0')])
        freeze_35 = ('3.5', [('dnspython3', '1.12.0')])

        freezes = [freeze_27, freeze_34]
        expected_freezes = [freeze_27, freeze_34, freeze_35]

        generate._clone_versions(freezes, options)

        self.assertEqual(expected_freezes, freezes)

    def test_py34_noclone_py35(self):
        # Simulate an environment where we have python 3.4 and python 3.5 data
        # so there is no need to clone.
        options = Namespace(version_map={'3.4': set(['3.5']),
                                         '3.5': set(['3.4'])})
        freeze_27 = ('2.7', [('dnspython', '1.15.0')])
        freeze_34 = ('3.4', [('dnspython3', '1.12.0')])
        freeze_35 = ('3.5', [('other-pkg', '1.0.0')])

        freezes = [freeze_27, freeze_34, freeze_35]
        expected_freezes = [freeze_27, freeze_34, freeze_35]

        generate._clone_versions(freezes, options)

        self.assertEqual(expected_freezes, freezes)

    def test_py35_clone_py34(self):
        # Simulate an environment where we have python 3.5 data and need to
        # clone that to python 3.4
        options = Namespace(version_map={'3.4': set(['3.5']),
                                         '3.5': set(['3.4'])})
        freeze_27 = ('2.7', [('dnspython', '1.15.0')])
        freeze_34 = ('3.4', [('dnspython3', '1.12.0')])
        freeze_35 = ('3.5', [('dnspython3', '1.12.0')])

        freezes = [freeze_27, freeze_35]
        expected_freezes = [freeze_27, freeze_35, freeze_34]

        generate._clone_versions(freezes, options)

        self.assertEqual(expected_freezes, freezes)

    def test_py35_clone_py34_py36(self):
        # Simulate an environment where we have python 3.5 data and need to
        # clone that to python 3.4
        options = Namespace(version_map={'3.5': set(['3.4', '3.6'])})
        freeze_27 = ('2.7', [('dnspython', '1.15.0')])
        freeze_34 = ('3.4', [('dnspython3', '1.12.0')])
        freeze_35 = ('3.5', [('dnspython3', '1.12.0')])
        freeze_36 = ('3.6', [('dnspython3', '1.12.0')])

        freezes = [freeze_27, freeze_35]
        expected_freezes = [freeze_27, freeze_35, freeze_34, freeze_36]

        generate._clone_versions(freezes, options)

        self.assertEqual(expected_freezes, freezes)
