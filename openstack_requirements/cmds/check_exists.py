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

"""Check to see if a package from a project's requrements file exist in g-r or
u-c.

"""

from __future__ import print_function

import argparse
import pkg_resources

from distutils.version import LooseVersion as LV

from openstack_requirements import requirement, project


def read_requirements_file(filename):
    with open(filename, 'rt') as f:
        body = f.read()
    return requirement.parse(body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'project',
        default='',
        help='path to the project source root folder.')
    parser.add_argument(
        '-u', '--upper-constraints',
        default='upper-constraints.txt',
        help='path to the upper-constraints.txt file')
    parser.add_argument(
        '-g', '--global-requirements',
        default='global-requirements.txt',
        help='Path to the global-requirements.txt file')
    parser.add_argument(
        '-b', '--blacklist',
        default='blacklist.txt',
        help='Path to the blacklist.txt file')
    args = parser.parse_args()

    upper_constraints = read_requirements_file(args.upper_constraints)
    global_requirements = read_requirements_file(args.global_requirements)
    blacklist = read_requirements_file(args.blacklist)
    project_data = project.read(args.project)
    error_count = 0

    for require_file, data in project_data.get('requirements', {}).items():
        print('\nComparing %s with global-requirements and upper-constraints'
              % require_file)
        requirements = requirement.parse(data)
        for name, spec_list in requirements.items():
            if not name or name in blacklist:
                continue
            if name not in global_requirements:
                print('%s from %s not found in global-requirements' % (
                       name, require_file))
                error_count += 1
                continue
            if name not in upper_constraints:
                print('%s from %s not found in upper-constraints' % (
                       name, require_file))
                error_count += 1
                continue
            elif spec_list:
                uc = upper_constraints[name][-1][-1]
                uc = pkg_resources.Requirement.parse(uc)
                uc_spec = uc.specs[0]
                for req, orig_line in spec_list:
                    specs = pkg_resources.Requirement.parse(orig_line).specs
                    for spec in specs:
                        if spec[0] in ['==', '>=']:
                            if LV((spec[1])) > LV(uc_spec[1]):
                                print(
                                    '%s must be <= %s from upper-constraints' %
                                    (name, uc_spec[1]))
                                error_count += 1
                                continue
                        elif spec[0] == '>':
                            if LV(spec[1]) >= LV(uc_spec[1]):
                                print(
                                    '%s must be < %s from upper-constraints' %
                                    (name, uc_spec[1]))
                                error_count += 1
                                continue

    return 1 if error_count else 0

