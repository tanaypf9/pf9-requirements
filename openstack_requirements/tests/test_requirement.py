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

import pkg_resources
import testscenarios
import testtools

from openstack_requirements import requirement


load_tests = testscenarios.load_tests_apply_scenarios


class TestParseRequirement(testtools.TestCase):

    dist_scenarios = [
        ('package', dict(
         line='swift',
         req=requirement.Requirement('swift', '', '', '', ''))),
        ('specifier', dict(
         line='alembic>=0.4.1',
         req=requirement.Requirement('alembic', '', '>=0.4.1', '', ''))),
        ('specifiers', dict(
         line='alembic>=0.4.1,!=1.1.8',
         req=requirement.Requirement('alembic', '', '!=1.1.8,>=0.4.1', '',
                                     ''))),
        ('comment-only', dict(
         line='# foo',
         req=requirement.Requirement('', '', '', '', '# foo'))),
        ('comment', dict(
         line='Pint>=0.5  # BSD',
         req=requirement.Requirement('Pint', '', '>=0.5', '', '# BSD'))),
        ('comment-with-semicolon', dict(
         line='Pint>=0.5  # BSD;fred',
         req=requirement.Requirement('Pint', '', '>=0.5', '', '# BSD;fred'))),
        ('case', dict(
         line='Babel>=1.3',
         req=requirement.Requirement('Babel', '', '>=1.3', '', ''))),
        ('markers', dict(
         line="pywin32;sys_platform=='win32'",
         req=requirement.Requirement('pywin32', '', '',
                                     "sys_platform=='win32'", ''))),
        ('markers-with-comment', dict(
         line="Sphinx<=1.2; python_version=='2.7'# Sadface",
         req=requirement.Requirement('Sphinx', '', '<=1.2',
                                     "python_version=='2.7'", '# Sadface')))]
    url_scenarios = [
        ('url', dict(
         line='file:///path/to/thing#egg=thing',
         req=requirement.Requirement('thing', 'file:///path/to/thing', '', '',
                                     ''),
         permit_urls=True)),
        ('editable', dict(
         line='-e file:///path/to/bar#egg=bar',
         req=requirement.Requirement('bar', '-e file:///path/to/bar', '', '',
                                     ''),
         permit_urls=True))]
    scenarios = dist_scenarios + url_scenarios

    def test_parse(self):
        parsed = requirement.parse_line(
            self.line, permit_urls=getattr(self, 'permit_urls', False))
        self.assertEqual(self.req, parsed)


class TestParseRequirementFailures(testtools.TestCase):

    scenarios = [
        ('url', dict(line='http://tarballs.openstack.org/oslo.config/'
                          'oslo.config-1.2.0a3.tar.gz#egg=oslo.config')),
        ('-e', dict(line='-e git+https://foo.com#egg=foo')),
        ('-f', dict(line='-f http://tarballs.openstack.org/'))]

    def test_does_not_parse(self):
        with testtools.ExpectedException(pkg_resources.RequirementParseError):
            requirement.parse_line(self.line)


class TestToContent(testtools.TestCase):

    def test_smoke(self):
        reqs = requirement.to_content(requirement.Requirements(
            [requirement.Requirement(
             'foo', '', '<=1', "python_version=='2.7'", '# BSD')]),
            marker_sep='!')
        self.assertEqual(
            ''.join(requirement._REQS_HEADER
                    + ["foo<=1!python_version=='2.7' # BSD\n"]),
            reqs)

    def test_location(self):
        reqs = requirement.to_content(requirement.Requirements(
            [requirement.Requirement(
             'foo', 'file://foo', '', "python_version=='2.7'", '# BSD')]))
        self.assertEqual(
            ''.join(requirement._REQS_HEADER
                    + ["file://foo#egg=foo;python_version=='2.7' # BSD\n"]),
            reqs)


class TestToReqs(testtools.TestCase):

    def test_editable(self):
        line = '-e file:///foo#egg=foo'
        reqs = list(requirement.to_reqs(line, permit_urls=True))
        req = requirement.Requirement('foo', '-e file:///foo', '', '', '')
        self.assertEqual(reqs, [(req, line)])

    def test_urls(self):
        line = 'file:///foo#egg=foo'
        reqs = list(requirement.to_reqs(line, permit_urls=True))
        req = requirement.Requirement('foo', 'file:///foo', '', '', '')
        self.assertEqual(reqs, [(req, line)])

    def test_not_urls(self):
        with testtools.ExpectedException(pkg_resources.RequirementParseError):
            list(requirement.to_reqs('file:///foo#egg=foo'))
