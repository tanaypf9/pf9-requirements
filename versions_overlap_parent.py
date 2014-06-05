#! /usr/bin/env python
# Copyright (C) 2011 OpenStack, LLC.
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
# Copyright (c) 2013 OpenStack Foundation
# Copyright 2014 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import subprocess

import pkg_resources


def increase_version(version_string):
    """Returns simple increased version string."""
    items = version_string.split('.')
    for i in range(len(items) - 1, 0, -1):
        current_item = items[i]
        if current_item.isdigit():
            current_item = int(current_item) + 1
            items[i] = str(current_item)
            break
    final = '.'.join(items)
    return final


def decrease_version(version_string):
    """Returns simple decreased version string."""
    items = version_string.split('.')
    for i in range(len(items) - 1, 0, -1):
        current_item = items[i]
        if current_item.isdigit():
            current_item = int(current_item) - 1
            if current_item >= 0:
                items[i] = str(current_item)
                break
            else:
                # continue to parent
                items[i] = '9'

    final = '.'.join(items)
    return final


def get_version_required(req):
    """Returns required version string depending on reqs."""
    operator = req[0]
    version = req[1]
    if operator == '>':
        version = increase_version(version)
    elif operator == '<':
        version = decrease_version(version)
    return version


class RequirementsList(object):
    def __init__(self, name):
        self.name = name
        self.reqs = {}

    def read_requirements(self, req_lines):
        """Read requirements."""
        for line in req_lines:
            if '#' in line:
                line = line[:line.find('#')]
            line = line.strip()
            if (not line or
                    line.startswith('http://tarballs.openstack.org/') or
                    line.startswith('-e') or
                    line.startswith('-f')):
                continue
            req = pkg_resources.Requirement.parse(line)
            self.reqs[req.project_name.lower()] = req


def compare_reqs(parent_reqs, head_reqs):
    failed = False
    for req in head_reqs.reqs.values():
        name = req.project_name.lower()
        parent_req = parent_reqs.reqs.get(name)
        if not parent_req:
            # head req didn't exist in parent reqs.
            continue

        if req == parent_req:
            # Requirement is the same, nothing to do.
            continue

        # check if overlaps
        for spec in req.specs:
            version = get_version_required(spec)
            if not parent_req.__contains__(version):
                failed = True
                print("Requirement %s does not overlap with parent " %
                      str(req))

    if failed:
        raise Exception("Problem with requirements, check previous output.")


class VersionsOverlapParent(object):
    def set_head_requirements(self, head_requirements):
        head_reqs = RequirementsList(name='HEAD')
        head_reqs.read_requirements(head_requirements)
        self._head_reqs = head_reqs

    def set_parent_requirements(self, parent_requirements):
        parent_reqs = RequirementsList(name='parent')
        parent_reqs.read_requirements(parent_requirements)
        self._parent_reqs = parent_reqs

    def compare_reqs(self):
        compare_reqs(self._parent_reqs, self._head_reqs)


def main():

    GLOBAL_REQUIREMENTS_FILENAME = 'global-requirements.txt'

    versions_overlap_parent = VersionsOverlapParent()

    # Parse current commit requirements list.
    with open(GLOBAL_REQUIREMENTS_FILENAME) as global_reqs:
        versions_overlap_parent.set_head_requirements(global_reqs)

    # Store the current branch
    git_head = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()

    # Check out the parent commit
    subprocess.check_output(['git', 'checkout', 'HEAD~1'])

    try:

        # Store parent commit requirements list.
        with open(GLOBAL_REQUIREMENTS_FILENAME) as global_reqs:
            versions_overlap_parent.set_parent_requirements(global_reqs)

    finally:

        # Switch back to the current commit
        subprocess.check_output(['git', 'checkout', git_head])

    versions_overlap_parent.compare_reqs()


if __name__ == '__main__':

    main()
