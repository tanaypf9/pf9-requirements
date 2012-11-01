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
A simple script to update the requirements files from the output of
the 'pip freeze' command.

The script can be called like this:

  $> pip freeze > frozen-requires.txt
  $> python freeze.py frozen-requires.txt

Any requirements listed in the target files will have their versions
updated to match the frozen requirements. The original versions are
included as comments in the file for reference.
"""

import os
import os.path
import sys

from pip import req


def _parse_reqs(filename):

    reqs = []

    pip_requires = open(filename, "r").readlines()
    for pip in pip_requires:
        pip = pip.strip()
        if pip.startswith("#") or len(pip) == 0:
            continue
        install_require = req.InstallRequirement.from_line(pip)
        if install_require.editable:
            reqs.append([pip, pip])
        elif install_require.url:
            reqs.append([pip, pip])
        else:
            reqs.append([install_require.req.key, pip])
    return reqs


def _freeze_requires(req, source_path):
    source_reqs = dict(_parse_reqs(source_path))

    dest_path = os.path.join('tools', req)

    dest_reqs = _parse_reqs(dest_path)
    dest_keys = [key.lower() for key, value in dest_reqs]
    dest_reqs = dict(dest_reqs)

    print "Syncing %s" % req
    with open(dest_path, 'w') as new_reqs:
        new_reqs.write("# These versions were frozen at release time\n")
        for old_require in dest_keys:
            new_reqs.write("%(source)s # %(dest)s\n" %
                           dict(source=source_reqs[old_require],
                                dest=dest_reqs[old_require]))


def main(argv):
    source_path = argv[0]
    for req in ('pip-requires', 'test-requires'):
        _freeze_requires(req, source_path)


if __name__ == "__main__":
    main(sys.argv[1:])
