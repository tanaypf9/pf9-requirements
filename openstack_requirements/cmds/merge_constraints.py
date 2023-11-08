import argparse
import sys

from pprint import pprint  # noqa

from openstack_requirements.cmds.generate import _combine_freezes
from openstack_requirements.cmds.generate import _make_sort_key
from openstack_requirements.cmds.generate import _parse_blacklist
from openstack_requirements.cmds.generate import _parse_freeze

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument( "-b","--blacklist", help="Filename of a list of package names to exclude.")
    parser.add_argument("-c", "--constraints", action="append", help="")
    args = parser.parse_args(argv or sys.argv[1:])
    freezes = []
    for constraint in args.constraints:
        (pyver, file) = constraint.split(':', 1)
        with open(file) as f:
            freeze = f.read()
        freezes.append((pyver, _parse_freeze(freeze)))
    blacklist = _parse_blacklist(args.blacklist)
    frozen = [*sorted(_combine_freezes(freezes, blacklist), key=_make_sort_key)]
    sys.stdout.writelines(frozen)
    sys.stdout.flush()
    return 0