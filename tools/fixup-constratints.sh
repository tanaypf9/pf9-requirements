#!/usr/bin/env bash

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script, when run from the root directory of this repository, will
# search the default and feature branches of all projects listed in the
# projects.txt file for declared dependencies, then output a list of any
# entries in the global-requirements.txt file which are not actual
# dependencies of those projects. Old dependencies which were removed
# from projects or which were used only for projects which have since
# been removed should be cleaned up, but many entries likely represent
# recent additions which still have pending changes to add them to one
# or more projects. In most cases, git pickaxe will yield the answer.

_base=$(pwd -P $(dirname $0)/..)

topic='feature/add-constraints-support'
repo=$1
change_nr=$2

if [ -z "$change_nr" ] ; then
    echo "$(basename "$0") repo change_nr" >&2
    exit 1
fi

cd $repo >/dev/null
if [ $? != 0 ] ; then
    echo Failed to cd to $repo >&2
    exit 1
fi

printf "Updating %-35s [ %6s ]\n" "$repo" "$change_nr"
git remote update
if git grep UPPER_CONSTRAINTS origin/master -- tox.ini ; then
    echo It looks like constraints support is already enabled
    exit 0
fi

git review -d "$change_nr"

[ -d tools ] || mkdir tools
cp -a ${_base}/tox-incubated/tox_install.sh tools/
chmod 0755 tools/tox_install.sh

git add tools/tox_install.sh
git ci --amend -C HEAD
git review -t "$topic"
