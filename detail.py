# -*- coding: utf-8 -*-

#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
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

from __future__ import print_function

import contextlib
import json
import os
import pkg_resources
import sys
import traceback
import urllib

try:
    PYPI_LOCATION = os.environ['PYPI_LOCATION']
except KeyError:
    PYPI_LOCATION = 'http://pypi.python.org/pypi'


KEEP_KEYS = frozenset([
    'author',
    'author_email',
    'maintainer',
    'maintainer_email',
    'license',
    'summary',
    'home_page',
])


def release_data(req):
    url = PYPI_LOCATION + "/%s/json" % (req.key)
    with contextlib.closing(urllib.urlopen(url)) as uh:
        if uh.getcode() != 200:
            raise IOError("Could not find data for %s (%s)"
                          % (req.key, uh.getcode()))
        return json.loads(uh.read())


def main():
    if len(sys.argv) == 1:
        print("%s requirement-file ..." % (sys.argv[0]), file=sys.stderr)
    for filename in sys.argv[1:]:
        print("Analyzing file: %s" % (filename))
        details = {}
        with open(filename, "rb") as fh:
            for line in fh.read().splitlines():
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                req = pkg_resources.Requirement.parse(line)
                print(" - processing: %s" % (req))
                try:
                    raw_req_data = release_data(req)
                except IOError:
                    traceback.print_exc()
                    details[req.key] = None
                else:
                    req_info = {}
                    for (k, v) in raw_req_data.get('info', {}).items():
                        if k not in KEEP_KEYS:
                            continue
                        req_info[k] = v
                    details[req.key] = {
                        'requirement': str(req),
                        'info': req_info,
                    }
        filename, _ext = os.path.splitext(filename)
        with open("%s.json" % (filename), "wb") as fh:
            fh.write(json.dumps(details, sort_keys=True, indent=4))


if __name__ == '__main__':
    main()
