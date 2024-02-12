# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys

from pprint import pprint  # noqa

from openstack_requirements.cmdlib import _combine_freezes
from openstack_requirements.cmdlib import _make_sort_key
from openstack_requirements.cmdlib import _parse_blacklist
from openstack_requirements.cmdlib import _parse_freeze


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--blacklist",
                        help="Filename of a list of package names to exclude.")
    parser.add_argument("-c", "--constraints", action="append", help="")
    args = parser.parse_args(argv or sys.argv[1:])
    freezes = []
    for constraint in args.constraints:
        (pyver, file) = constraint.split(':', 1)
        with open(file) as f:
            freeze = f.read()
        freezes.append((pyver, _parse_freeze(freeze)))
    blacklist = _parse_blacklist(args.blacklist)
    frozen = [*sorted(_combine_freezes(freezes, blacklist),
                      key=_make_sort_key)]
    sys.stdout.writelines(frozen)
    sys.stdout.flush()
    return 0
