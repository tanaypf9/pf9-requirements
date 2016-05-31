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

"""Apply validation rules to the various requirements lists.

"""

import argparse

import pkg_resources

from openstack_requirements import requirement


def read_requirements_file(filename):
    with open(filename, 'rt') as f:
        body = f.read()
    return requirement.parse(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'upper_constraints',
        default='upper-constraints.txt',
        help='path to the upper-constraints.txt file',
    )
    args = parser.parse_args()

    print('\nChecking %s' % args.upper_constraints)
    upper_constraints = read_requirements_file(args.upper_constraints)
    for name, spec_list in upper_constraints.items():
        print('\nChecking conflicts for %s' % name)
        pkg_resources.require(name)
