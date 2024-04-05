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

import os

GLOBAL_REQS = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    'global-requirements.txt',
)


def main():
    sections = {}
    deps = []
    section = ''
    comment = ''

    with open(GLOBAL_REQS) as fh:
        for line in fh.readlines():
            if not line.strip():
                continue

            if line.startswith('## section:'):
                if section:
                    sections[section] = sorted(
                        deps, key=lambda x: x[0].lower()
                    )
                    deps = []

                section = line.removeprefix('## section:')
                continue

            if line.startswith('#'):
                comment += line
                continue

            deps.append((line, comment or None))
            comment = ''

    sections[section] = sorted(
        deps, key=lambda x: x[0].lower()
    )

    with open(GLOBAL_REQS, 'w') as fh:
        for i, section in enumerate(sections):
            if i != 0:
                fh.write('\n')

            fh.write(f'## section:{section}\n')

            for dep, comment in sections[section]:
                if comment:
                    fh.write(comment)

                fh.write(dep)


if __name__ == '__main__':
    main()
