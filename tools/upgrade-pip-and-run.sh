#!/bin/bash -e
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
#
# Constraints uses features only recently added to pip and as we cannot
# control the version of virtualenv installed in the environment tox is
# executed from, we need this shim to upgrade the pip in the tox venv.
#
# pip introduced constraints in 7.1.0
# setuptools 17.1.0 contains fixes to environment markers

pipCommand="$@"
pip install "pip>=7.1.0" "setuptools>=17.1.0"
pip ${pipCommand}
