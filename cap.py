#! /usr/bin/env python

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

import argparse
import re


def cap(requirements, freeze):
    """Cap requirements to version in freeze.

    Input: two arrays of lines.
    Output: Array of new lines.
    """
    output = []
    for line in requirements:
        if ("<" not in line
                and "==" not in line
                and not line.startswith('#')
                and not line.startswith('-e')
                and not len(line) is 0):
            # add cap
            new_cap = cap_requirement(split(line)[0], freeze)
            if new_cap:
                output.append(append_cap(line, new_cap))
            else:
                output.append(line)
        else:
            output.append(line)
    return output


def append_cap(line, new_cap):
    start = line
    end = None
    if "#" in line:
        # if comment
        parts = line.split(' #')
        start = parts[0].strip()
        end = parts[1]
    if len(split(start)) > 1:
        # cap format
        op = ",<="
    else:
        op = "<="
    if end:
        return "%s%s%s #%s" % (start, op, new_cap, end)
    else:
        return "%s%s%s" % (line, op, new_cap)


def split(line):
    return re.split('[><=]', line)


def cap_requirement(requirement, freeze):
    for line in freeze:
        if requirement in line and not line.startswith('-e '):
            return split(line)[-1]
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('requirements', help='requirements file input')
    parser.add_argument('freeze', help='output of pip freeze')
    args = parser.parse_args()
    with open(args.requirements) as f:
        requirements = [line.strip() for line in f.readlines()]
    with open(args.freeze) as f:
        freeze = [line.strip() for line in f.readlines()]
    for line in cap(requirements, freeze):
        print(line)

if __name__ == '__main__':
    main()
