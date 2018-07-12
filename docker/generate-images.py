#!/usr/bin/env python3

import os
import shutil
import subprocess

# TODO: make this gate friendly
# TODO: work out the minimum set of packages to get lsb-rlease to work
TEMPLATE = """ FROM python:%(python_version)s-stretch
COPY global-requirements.txt /
COPY bindep.txt /

RUN apt-get update
RUN apt-get install -y lsb lsb-release

RUN pip install -U pip setuptools wheel bindep
RUN apt-get install -y $(bindep -b)

RUN pip install -r /global-requirements.txt

CMD pip freeze
"""
GR_FILE = 'global-requirements.txt'

starting_dir = os.getcwd()
os.chdir('docker')
# for python_version in ['2.7', '3.4', '3.5', '3.6']:
for python_version in ['2.7', '3.5']:
    if not os.path.isdir(python_version):
        os.makedirs(python_version)
    os.chdir(python_version)
    params = dict(python_version=python_version)

    with open('Dockerfile', 'w') as f:
        f.write(TEMPLATE % (params))

    for _file in ['global-requirements.txt', 'bindep.txt']:
        shutil.copyfile(os.path.join(starting_dir, _file), _file)

    subprocess.run(['docker', 'build', '--tag',
                    'requirements:%s' % (python_version), '.'],
                   check=False)
