#!/usr/bin/python
#
# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
import datetime
import json
import sys
import urllib2

import pip.req


class Release(object):
    name = ""
    version = ""
    filename = ""
    released = ""

    def __init__(self, name, version, filename, released):
        self.name = name
        self.version = version
        self.filename = filename
        self.released = released

    def __repr__(self):
        return "<Released %s %s %s>" % (self.name, self.version, self.released)


def _parse_pypi_released(datestr):
    return datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")


def _parse_pip(line):
    install_require = pip.req.InstallRequirement.from_line(line)
    if install_require.editable:
        return pip
    elif install_require.url:
        return pip
    else:
        return install_require.req.key


def get_requirements():
    reqs = []
    with open('global-requirements.txt') as f:
        for line in f.readlines():
            if not line or line.startswith('#') or line.startswith('\n'):
                continue
            reqs.append(_parse_pip(line))
    return reqs


def get_releases_for_package(name, since):
    f = urllib2.urlopen("http://pypi.python.org/pypi/%s/json" % name)
    jsondata = f.read()
    data = json.loads(jsondata)
    releases = []
    for relname, rellist in data['releases'].iteritems():
        for rel in rellist:
            if rel['python_version'] == 'source':
                when = _parse_pypi_released(rel['upload_time'])
                # for speed, only care about when > since
                if when < since:
                    continue

                releases.append(
                    Release(
                        name,
                        relname,
                        rel['filename'],
                        when))
                break
    return releases


def get_releases_since(reqs, since):
    all_releases = []
    for req in reqs:
        all_releases.extend(get_releases_for_package(req, since))
    sorted_releases = sorted(all_releases,
                             key=lambda x: x.released,
                             reverse=True)
    return sorted_releases


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'List recent releases of items in global requirements '
            'to look for possible breakage'))
    parser.add_argument('-s', '--since', type=int,
                        default=14,
                        help='look back ``since`` days (default 14)')
    return parser.parse_args()


def main():
    opts = parse_args()
    since = datetime.datetime.today() - datetime.timedelta(days=opts.since)
    print("Looking for requirements releases since %s" % since)
    reqs = get_requirements()
    # additional sensitive requirements
    reqs.append('tox')
    releases = get_releases_since(reqs, since)
    for rel in releases:
        print(rel)


if __name__ == '__main__':
    sys.exit(main())
