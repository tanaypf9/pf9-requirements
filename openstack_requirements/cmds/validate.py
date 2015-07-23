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

from openstack_requirements import constraints
from openstack_requirements import requirement


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'global_requirements',
        default='global-requirements.txt',
        help='path to the global-requirements.txt file',
    )
    parser.add_argument(
        'upper_constraints',
        default='upper-constraints.txt',
        help='path to the upper-constraints.txt file',
    )
    parser.add_argument(
        'blacklist',
        default='blacklist.txt',
        help='path to the blacklist.txt file',
    )
    args = parser.parse_args()

    error_count = 0

    # Check the format of the constraints file.
    print('\nChecking %s' % args.upper_constraints)
    constraints_content = open(args.upper_constraints, 'rt').read()
    upper_constraints = requirement.parse(constraints_content)
    for msg in constraints.check_format(upper_constraints):
        print(msg)
        error_count += 1

    # Check that the constraints and requirements are compatible.
    print('\nChecking %s' % args.global_requirements)
    global_req_content = open(args.global_requirements, 'rt').read()
    global_reqs = requirement.parse(global_req_content)
    for msg in constraints.check_compatible(global_reqs, upper_constraints):
        print(msg)
        error_count += 1

    # Check that all of the items in the global-requirements list
    # appear in exactly one of the constraints file or the blacklist.
    print('\nChecking %s' % args.blacklist)
    blacklist_content = open(args.blacklist, 'rt').read()
    blacklist = requirement.parse(blacklist_content)
    for msg in constraints.check_blacklist_coverage(global_reqs,
                                                    upper_constraints,
                                                    blacklist,
                                                    'upper-constraints.txt'):
        print(msg)
        error_count += 1

    return 1 if error_count else 0
