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

import os.path
import shutil

import fixtures


def _file_to_list(fname):
    with open(fname) as f:
        content = list(map(lambda x: x.rstrip(), f.readlines()))
        print(content)
        return content


class UpdateEnvironment(fixtures.Fixture):
    """An environment where update.py can be run."""

    def setUp(self):
        super(UpdateEnvironment, self).setUp()
        self.dir = self.useFixture(fixtures.TempDir()).path
        # test_update uses all three; test_update_suffix doesn't use bad;
        # test_update_pbr only uses pbr.
        self.project_dir = os.path.join(self.dir, "project")
        self.bad_project_dir = os.path.join(self.dir, "bad_project")
        self.oslo_dir = os.path.join(self.dir, "project_with_oslo")
        self.pbr_dir = os.path.join(self.dir, "project_pbr")

        self.req_file = os.path.join(self.dir, "global-requirements.txt")
        self.proj_file = os.path.join(self.project_dir, "requirements.txt")
        self.oslo_file = os.path.join(self.oslo_dir, "requirements.txt")
        self.pbr_file = os.path.join(self.pbr_dir, "requirements.txt")

        self.bad_proj_file = os.path.join(
            self.bad_project_dir, "requirements.txt")
        self.proj_test_file = os.path.join(
            self.project_dir, "test-requirements.txt")
        self.pbr_test_file = os.path.join(
            self.pbr_dir, "test-requirements.txt")

        self.setup_file = os.path.join(self.project_dir, "setup.py")
        self.old_setup_file = os.path.join(self.oslo_dir, "setup.py")
        self.bad_setup_file = os.path.join(self.bad_project_dir, "setup.py")
        self.pbr_setup_file = os.path.join(self.pbr_dir, "setup.py")
        self.setup_cfg_file = os.path.join(self.project_dir, "setup.cfg")
        self.bad_setup_cfg_file = os.path.join(
            self.bad_project_dir, "setup.cfg")
        self.oslo_setup_cfg_file = os.path.join(self.oslo_dir, "setup.cfg")
        self.pbr_setup_cfg_file = os.path.join(self.pbr_dir, "setup.cfg")
        os.mkdir(self.project_dir)
        os.mkdir(self.oslo_dir)
        os.mkdir(self.bad_project_dir)
        os.mkdir(self.pbr_dir)

        shutil.copy("tests/files/gr-base.txt", self.req_file)
        shutil.copy("tests/files/project-with-oslo-tar.txt", self.oslo_file)
        shutil.copy("tests/files/project.txt", self.proj_file)
        shutil.copy(
            "tests/files/project-with-bad-requirement.txt", self.bad_proj_file)
        shutil.copy("tests/files/project.txt", self.pbr_file)
        shutil.copy("tests/files/test-project.txt", self.proj_test_file)
        shutil.copy("tests/files/test-project.txt", self.pbr_test_file)
        shutil.copy("tests/files/setup.py", self.setup_file)
        shutil.copy("tests/files/setup.py", self.bad_setup_file)
        shutil.copy("tests/files/old-setup.py", self.old_setup_file)
        shutil.copy("tests/files/setup.py", self.pbr_setup_file)
        shutil.copy("tests/files/setup.cfg", self.setup_cfg_file)
        shutil.copy("tests/files/setup.cfg", self.bad_setup_cfg_file)
        shutil.copy("tests/files/setup.cfg", self.oslo_setup_cfg_file)
        shutil.copy("tests/files/pbr_setup.cfg", self.pbr_setup_cfg_file)
        shutil.copy("update.py", os.path.join(self.dir, "update.py"))
