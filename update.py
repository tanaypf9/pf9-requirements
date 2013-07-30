# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack, LLC
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

r"""
A simple script to update the requirements files from a global set of
allowable requirements.

The script can be called like this:

  $> python update.py ../myproj

Any requirements listed in the target files will have their versions
updated to match the global requirements. Requirements not in the global
files will be dropped.
"""

import os
import os.path
import sys

from pip import req


def _mod_to_path(mod):
    return os.path.join(*mod.split('.'))


def _dest_path(path, base, dest_dir):
    return os.path.join(dest_dir, _mod_to_path(base), path)


def _parse_reqs(filename):

    reqs = dict()

    pip_requires = open(filename, "r").readlines()
    for pip in pip_requires:
        pip = pip.strip()
        if pip.startswith("#") or len(pip) == 0:
            continue
        install_require = req.InstallRequirement.from_line(pip)
        if install_require.editable:
            reqs[pip] = pip
        elif install_require.url:
            reqs[pip] = pip
        else:
            reqs[install_require.req.key] = pip
    return reqs


def _sync_requirements_file(source_reqs, dest_path):
    dest_reqs = []
    with open(dest_path, 'r') as dest_reqs_file:
        dest_reqs = dest_reqs_file.readlines()

    print "Syncing %s" % dest_path

    with open(dest_path, 'w') as new_reqs:
        new_reqs.write("# This file is managed by openstack-depends\n")
        for old_require in dest_keys:
            # Special cases:
            # versions of our stuff from tarballs.openstack.org are ok
            # projects need to align pep8 version on their own time
            if old_require in source_reqs or \
                "http://tarballs.openstack.org" in old_require:
                new_reqs.write("%s\n" % source_reqs[old_require])
            if "pep8" in old_require:
                new_reqs.write("%s\n" % dest_reqs[old_require])

def _copy_requires(source_path, dest_dir):
    """Copy requirements files."""

    source_reqs = _parse_reqs(source_path)

    target_files = (
        'requirements.txt', 'tools/pip-requires',
        'test-requirements.txt', 'tools/test-requires')

    for dest in target_files:
        dest_path = os.path.join(dest_dir, dest)
        if os.path.exists(dest_path):
            print "_sync_requirements_file(%s, %s)" % (source_reqs, dest_path)
            _sync_requirements_file(source_reqs, dest_path)


def main(argv):
    _copy_requires('global-requirements.txt', argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
