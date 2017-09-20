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

[ -d publish ] || mkdir publish

# NOTE(tonyb): Publish EOL'd constraints files.  We do this here as a quick way
# to publish the data.  It can be removed anytime after the first successful run
declare -a old_branches=(juno-eol kilo-eol liberty-eol mitaka-eol)

for tag in ${old_branches[@]} ; do
    # trim the '-eol'
    series=${tag::-4}
    git show ${tag}:upper-constraints.txt > publish/${series}.txt
done

# NOTE(tonyb): Publish current branches.  This can be reduced as we land this
# script on stable/* branches
declare -a current_branches=(stable/newton stable/ocata stable/pike)
for branch in ${current_branches[@]} ; do
    series=$(basename "$branch")
    git show origin/${branch}:upper-constraints.txt > publish/${series}.txt
done

for series in master queens ; do
    git show origin/master:upper-constraints.txt > publish/${series}.txt
done
