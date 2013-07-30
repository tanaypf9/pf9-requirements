# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

import os
import os.path
import re
import shutil
import subprocess
import tempfile
import testtools


class UpdateTest(testtools.TestCase):

    def setUp(self):
        super(UpdateTest, self).setUp()
        self.dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.dir, "project")
        self.oslo_dir = os.path.join(self.dir, "project_with_oslo")

        self.req_file = os.path.join(self.dir, "requirements.txt")
        self.proj_file = os.path.join(self.project_dir, "requirements.txt")
        self.oslo_file = os.path.join(self.oslo_dir, "requirements.txt")
        os.mkdir(self.project_dir)
        os.mkdir(self.oslo_dir)
        shutil.copy("tests/files/gr-base.txt", self.req_file)
        shutil.copy("tests/files/project-with-oslo-tar.txt", self.oslo_file)
        shutil.copy("tests/files/project.txt", self.proj_file)
        shutil.copy("update.py", os.path.join(self.dir, "update.py"))

        # now go call update and see what happens
        os.chdir(self.dir)
        subprocess.call("python update.py project")
        subprocess.call("python update.py project_with_oslo")

    def test_requirements(self):
        with open(self.req_file) as f:
            content = f.readlines()
            self.assertIn("jsonschema>=1.0.0,!=1.4.0,<2", content)

    def test_project_with_oslo(self):
        with open(self.oslo_file) as f:
            content = f.readlines()
            self.assertIn("jsonschema>=1.0.0,!=1.4.0,<2", content)
