# Copyright 2013 IBM Corp.
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

import os.path
import StringIO

import fixtures
import testtools

from tests import common
import update


class UpdateTest(testtools.TestCase):

    def _init_env(self):
        self.env = self.useFixture(common.UpdateEnvironment())
        self.project_dir = self.env.project_dir
        self.bad_project_dir = self.env.bad_project_dir
        self.oslo_dir = self.env.oslo_dir

        self.req_file = self.env.req_file
        self.proj_file = self.env.proj_file
        self.oslo_file = self.env.oslo_file
        self.bad_proj_file = self.env.bad_proj_file
        self.proj_test_file = self.env.proj_test_file
        self.setup_file = self.env.setup_file
        self.old_setup_file = self.env.old_setup_file
        self.bad_setup_file = self.env.bad_setup_file
        self.setup_cfg_file = self.env.setup_cfg_file
        self.bad_setup_cfg_file = self.env.bad_setup_cfg_file
        self.oslo_setup_cfg_file = self.env.oslo_setup_cfg_file

    def _run_update(self):
        # now go call update and see what happens
        update.main([self.env.project.root])
        update.main([self.env.oslo_project.root])

    def setUp(self):
        super(UpdateTest, self).setUp()
        self._init_env()
        # for convenience put us in the directory with the update.py
        self.addCleanup(os.chdir, os.path.abspath(os.curdir))
        os.chdir(self.env.dir)

    def test_requirements(self):
        self._run_update()
        reqs = common._file_to_list(self.req_file)
        self.assertIn("jsonschema>=1.0.0,!=1.4.0,<2", reqs)

    def test_project(self):
        self._run_update()
        reqs = common._file_to_list(self.proj_file)
        # ensure various updates take
        self.assertIn("jsonschema>=1.0.0,!=1.4.0,<2", reqs)
        self.assertIn("python-keystoneclient>=0.4.1", reqs)
        self.assertIn("SQLAlchemy>=0.7,<=0.7.99", reqs)

    def test_requirements_header(self):
        self._run_update()
        _REQS_HEADER = [
            '# The order of packages is significant, because pip processes '
            'them in the order',
            '# of appearance. Changing the order has an impact on the overall '
            'integration',
            '# process, which may cause wedges in the gate later.',
        ]
        reqs = common._file_to_list(self.proj_file)
        self.assertEqual(_REQS_HEADER, reqs[:3])

    def test_project_with_oslo(self):
        self._run_update()
        reqs = common._file_to_list(self.oslo_file)
        oslo_tar = ("-f http://tarballs.openstack.org/oslo.config/"
                    "oslo.config-1.2.0a3.tar.gz#egg=oslo.config-1.2.0a3")
        self.assertIn(oslo_tar, reqs)

    def test_test_project(self):
        self._run_update()
        reqs = common._file_to_list(self.proj_test_file)
        self.assertIn("testtools>=0.9.32", reqs)
        self.assertIn("testrepository>=0.0.17", reqs)
        # make sure we didn't add something we shouldn't
        self.assertNotIn("sphinxcontrib-pecanwsme>=0.2", reqs)

    def test_install_setup(self):
        self._run_update()
        setup_contents = common._file_to_list(self.setup_file)
        self.assertIn("# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO"
                      " - DO NOT EDIT", setup_contents)

    def test_no_install_setup(self):
        self._run_update()
        setup_contents = common._file_to_list(self.old_setup_file)
        self.assertNotIn(
            "# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO"
            " - DO NOT EDIT", setup_contents)

    # These are tests which don't need to run the project update in advance
    def test_requirment_not_in_global(self):
        with testtools.ExpectedException(Exception):
            update.main([self.env.bad_project.root])

    def test_requirment_not_in_global_non_fatal(self):
        self.useFixture(
            fixtures.EnvironmentVariable("NON_STANDARD_REQS", "1"))
        update.main([self.env.bad_project.root])

    def test_requirement_soft_update(self):
        update.main(["-s", self.env.bad_project.root])
        reqs = common._file_to_list(self.bad_proj_file)
        self.assertIn("thisisnotarealdepedency", reqs)

    # testing output
    def test_non_verbose_output(self):
        capture = StringIO.StringIO()
        update.main([self.env.project.root], capture)
        expected = ('Version change for: greenlet, sqlalchemy, eventlet, pastedeploy, routes, webob, wsgiref, boto, kombu, pycrypto, python-swiftclient, lxml, jsonschema, python-keystoneclient\n'  # noqa
            """Updated %(project)s/requirements.txt:
    greenlet>=0.3.1                ->   greenlet>=0.3.2
    SQLAlchemy>=0.7.8,<=0.7.99     ->   SQLAlchemy>=0.7,<=0.7.99
    eventlet>=0.9.12               ->   eventlet>=0.12.0
    PasteDeploy                    ->   PasteDeploy>=1.5.0
    routes                         ->   Routes>=1.12.3
    WebOb>=1.2                     ->   WebOb>=1.2.3,<1.3
    wsgiref                        ->   wsgiref>=0.1.2
    boto                           ->   boto>=2.4.0
    kombu>2.4.7                    ->   kombu>=2.4.8
    pycrypto>=2.1.0alpha1          ->   pycrypto>=2.6
    python-swiftclient>=1.2,<2     ->   python-swiftclient>=1.2
    lxml                           ->   lxml>=2.3
    jsonschema                     ->   jsonschema>=1.0.0,!=1.4.0,<2
    python-keystoneclient>=0.2.0   ->   python-keystoneclient>=0.4.1
Version change for: mox, mox3, testrepository, testtools
Updated %(project)s/test-requirements.txt:
    mox==0.5.3                     ->   mox>=0.5.3
    mox3==0.7.3                    ->   mox3>=0.7.0
    testrepository>=0.0.13         ->   testrepository>=0.0.17
    testtools>=0.9.27              ->   testtools>=0.9.32
""") % dict(project=self.env.project.root)
        self.assertEqual(expected, capture.getvalue())

    def test_verbose_output(self):
        capture = StringIO.StringIO()
        update.main(['-v', self.env.project.root], capture)
        expected = ("""Syncing %(project)s/requirements.txt
Version change for: greenlet, sqlalchemy, eventlet, pastedeploy, routes, webob, wsgiref, boto, kombu, pycrypto, python-swiftclient, lxml, jsonschema, python-keystoneclient\n"""  # noqa
            """Updated %(project)s/requirements.txt:
    greenlet>=0.3.1                ->   greenlet>=0.3.2
    SQLAlchemy>=0.7.8,<=0.7.99     ->   SQLAlchemy>=0.7,<=0.7.99
    eventlet>=0.9.12               ->   eventlet>=0.12.0
    PasteDeploy                    ->   PasteDeploy>=1.5.0
    routes                         ->   Routes>=1.12.3
    WebOb>=1.2                     ->   WebOb>=1.2.3,<1.3
    wsgiref                        ->   wsgiref>=0.1.2
    boto                           ->   boto>=2.4.0
    kombu>2.4.7                    ->   kombu>=2.4.8
    pycrypto>=2.1.0alpha1          ->   pycrypto>=2.6
    python-swiftclient>=1.2,<2     ->   python-swiftclient>=1.2
    lxml                           ->   lxml>=2.3
    jsonschema                     ->   jsonschema>=1.0.0,!=1.4.0,<2
    python-keystoneclient>=0.2.0   ->   python-keystoneclient>=0.4.1
Syncing %(project)s/test-requirements.txt
Version change for: mox, mox3, testrepository, testtools
Updated %(project)s/test-requirements.txt:
    mox==0.5.3                     ->   mox>=0.5.3
    mox3==0.7.3                    ->   mox3>=0.7.0
    testrepository>=0.0.13         ->   testrepository>=0.0.17
    testtools>=0.9.27              ->   testtools>=0.9.32
Syncing setup.py
""") % dict(project=self.env.project.root)
        self.assertEqual(expected, capture.getvalue())
