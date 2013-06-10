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


def _parse_pip(pip):

    install_require = req.InstallRequirement.from_line(pip)
    if install_require.editable:
        return pip
    elif install_require.url:
        return pip
    else:
        return install_require.req.key


def _parse_reqs(filename):

    reqs = dict()

    pip_requires = open(filename, "r").readlines()
    for pip in pip_requires:
        pip = pip.strip()
        if pip.startswith("#") or len(pip) == 0:
            continue
        reqs[_parse_pip(pip)] = pip
    return reqs


def _copy_requires(req, source_paths, dest_dir):
    """Copy requirements files."""

    dest_path = os.path.join(dest_dir, req)

    if not os.path.exists(dest_path):
        # This can happen, we try all paths
        return

    source_reqs = dict()
    for s in source_paths:
        source_reqs.update(_parse_reqs(s))

    dest_reqs = open(dest_path, 'r')
    print "Syncing %s" % req

    with open(dest_path+".new", 'w') as new_reqs:
        for old_require in dest_reqs:
            # copy comments
            if old_require[0] == '#':
                new_reqs.write(old_require)
                continue
            old_require = old_require.rstrip().lower()
            if len(old_require) == 0:
                continue
            old_pip = _parse_pip(old_require)

            # Special cases:
            # projects need to align pep8 version on their own time
            if "pep8" in old_pip:
                new_reqs.write("%s\n" % old_require)
                continue
            # versions of our stuff from tarballs.openstack.org are ok
            if "http://tarballs.openstack.org/" in old_pip:
                new_reqs.write("%s\n" % old_require)
                continue

            if old_pip in source_reqs:
                new_reqs.write("%s\n" % source_reqs[old_pip])

    dest_reqs.close()
    os.unlink(dest_path)
    os.rename(dest_path+".new", dest_path)


def main(argv):
    for req in ('tools/pip-requires', 'requirements.txt'):
        _copy_requires(req, ['tools/pip-requires'], argv[0])

    for req in ('tools/test-requires', 'test-requirements.txt'):
        _copy_requires(req,
                       ['tools/pip-requires', 'tools/test-requires'],
                       argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
