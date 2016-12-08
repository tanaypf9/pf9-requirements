#!/usr/bin/env python

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import print_function

import ConfigParser
import importlib
import re
import sys


def main():
    errors = 0
    pattern = re.compile('^(.*?)\s*=\s*([^:]*?):.*$')
    config = ConfigParser.ConfigParser()
    config.read('setup.cfg')
    console_scripts = config.get('entry_points', 'console_scripts')
    for script in console_scripts.split('\n'):
        match = pattern.match(script)
        if match:
            (script, module) = match.groups()
            try:
                importlib.import_module(module)
            except ImportError as err:
                print('Imports for %s failed:\n\t%s' % (script, err))
                errors += 1
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
