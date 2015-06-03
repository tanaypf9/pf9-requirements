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

import testtools

from tests import common
import update


class UpdateTestWithSuffix(testtools.TestCase):

    def setUp(self):
        super(UpdateTestWithSuffix, self).setUp()
        self._init_env()
        # for convenience put us in the directory with the update.py
        self.addCleanup(os.chdir, os.path.abspath(os.curdir))
        os.chdir(self.env.dir)
        # now go call update and see what happens
        update.main(['-o', 'global', self.env.project.root])
        update.main(['-o', 'global', self.env.oslo_project.root])

    def _init_env(self):
        self.env = self.useFixture(common.UpdateEnvironment())
        self.project_dir = self.env.project_dir
        self.oslo_dir = self.env.oslo_dir

        self.req_file = self.env.req_file
        self.proj_file = self.env.proj_file
        self.oslo_file = self.env.oslo_file
        self.proj_test_file = self.env.proj_test_file
        self.setup_file = self.env.setup_file
        self.old_setup_file = self.env.old_setup_file
        self.setup_cfg_file = self.env.setup_cfg_file
        self.oslo_setup_cfg_file = self.env.oslo_setup_cfg_file

    def test_requirements(self):
        # this is the sanity check test
        reqs = common._file_to_list(self.req_file)
        self.assertIn("jsonschema>=1.0.0,!=1.4.0,<2", reqs)

    def test_project(self):
        reqs = common._file_to_list("%s.%s" % (self.proj_file, 'global'))
        # ensure various updates take
        self.assertIn("jsonschema>=1.0.0,!=1.4.0,<2", reqs)
        self.assertIn("python-keystoneclient>=0.4.1", reqs)
        self.assertIn("SQLAlchemy>=0.7,<=0.7.99", reqs)

    def test_project_with_oslo(self):
        reqs = common._file_to_list("%s.%s" % (self.oslo_file, 'global'))
        oslo_tar = ("-f http://tarballs.openstack.org/oslo.config/"
                    "oslo.config-1.2.0a3.tar.gz#egg=oslo.config-1.2.0a3")
        self.assertIn(oslo_tar, reqs)

    def test_test_project(self):
        reqs = common._file_to_list("%s.%s" % (self.proj_test_file, 'global'))
        self.assertIn("testtools>=0.9.32", reqs)
        self.assertIn("testrepository>=0.0.17", reqs)
        # make sure we didn't add something we shouldn't
        self.assertNotIn("sphinxcontrib-pecanwsme>=0.2", reqs)

    def test_install_setup(self):
        setup_contents = common._file_to_list(self.setup_file)
        self.assertIn("# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO"
                      " - DO NOT EDIT", setup_contents)

    def test_no_install_setup(self):
        setup_contents = common._file_to_list(self.old_setup_file)
        self.assertNotIn(
            "# THIS FILE IS MANAGED BY THE GLOBAL REQUIREMENTS REPO"
            " - DO NOT EDIT", setup_contents)
