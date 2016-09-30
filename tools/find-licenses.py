#!/usr/bin/env python

import re
import sys
import xmlrpclib

import yaml

def main():
    packages = {}
    for line in open(sys.argv[1]):
        line = line.strip().split(';')[0]
        (package, release) = re.match('(.*)===(.*)', line).groups()
        client = xmlrpclib.ServerProxy('https://pypi.org/pypi')
        release_data = client.release_data(package, release)
        license = release_data.get('license')
        classifiers = release_data.get('classifiers')
        if classifiers:
            trove_licenses = [
                    x[11:] for x in classifiers if x.startswith('License :')]
        else:
            trove_licenses = None
        if trove_licenses:
            packages[line] = trove_licenses
        else:
            packages[line] = [license]
    print(yaml.safe_dump(
        packages, allow_unicode=True, default_flow_style=False))

if __name__ == '__main__':
    main()
