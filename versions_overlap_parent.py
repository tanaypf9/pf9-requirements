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

import os
import os.path
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
        self.failed = False

    def read_requirements(self, fn, ignore_dups=False, strict=False):
        """Read a requirements file and optionally enforce style."""
        if not os.path.exists(fn):
            return
        for line in open(fn):
            if strict and '\n' not in line:
                raise Exception("Requirements file %s does not "
                                "end with a newline." % fn)
            if '#' in line:
                line = line[:line.find('#')]
            line = line.strip()
            if (not line or
                    line.startswith('http://tarballs.openstack.org/') or
                    line.startswith('-e') or
                    line.startswith('-f')):
                continue
            req = pkg_resources.Requirement.parse(line)
            if (not ignore_dups and strict and req.project_name.lower()
                    in self.reqs):
                print("Duplicate requirement in %s: %s" %
                      (self.name, str(req)))
                self.failed = True
            self.reqs[req.project_name.lower()] = req

    def read_all_requirements(self, global_req=False, include_dev=False,
                              strict=False):
        """Read all the requirements into a list.

        Build ourselves a consolidated list of requirements. If global_req is
        True then we are parsing the global requirements file only, and
        ensure that we don't parse it's test-requirements.txt erroneously.

        If include_dev is true allow for development requirements, which
        may be prereleased versions of libraries that would otherwise be
        listed. This is most often used for olso prereleases.

        If strict is True then style checks should be performed while reading
        the file.
        """
        if global_req:
            self.read_requirements('global-requirements.txt', strict=strict)
        else:
            for fn in ['tools/pip-requires',
                       'tools/test-requires',
                       'requirements.txt',
                       'test-requirements.txt'
                       ]:
                self.read_requirements(fn, strict=strict)
        if include_dev:
            self.read_requirements('dev-requirements.txt',
                                   ignore_dups=True, strict=strict)


def compare_reqs(parent_reqs, head_reqs):
    failed = False
    for req in head_reqs.reqs.values():
        name = req.project_name.lower()
        if name in parent_reqs.reqs:
            if req == parent_reqs.reqs[name]:
                # Requirement is the same, nothing to do.
                continue

            # check if overlaps
            for spec in req.specs:
                version = get_version_required(spec)
                parent_req = parent_reqs.reqs[name]
                if not parent_req.__contains__(version):
                    failed = True
                    print("Requirement %s does not overlap with parent " %
                          str(req))

    if failed:
        raise Exception("Problem with requirements, check previous output.")


def main():

    # Store the current branch
    git_head = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()

    # Check out the parent commit
    subprocess.check_output(['git', 'checkout', 'HEAD~1'])

    # Store parent commit requirements list.
    parent_reqs = RequirementsList(name='parent')
    parent_reqs.read_requirements('global-requirements.txt')

    # Switch back to the current commit
    subprocess.check_output(['git', 'checkout', git_head])

    # Parse current commit requirements list.
    head_reqs = RequirementsList(name='HEAD')
    head_reqs.read_requirements('global-requirements.txt')

    compare_reqs(parent_reqs, head_reqs)


main()
