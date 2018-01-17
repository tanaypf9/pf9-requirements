#!/bin/bash
#
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

if [[ $# -ne 1 ]]; then
    cat - <<EOF
$0 NAME [BRANCH...]

  Show the version of NAME used in each BRANCH. If no branches are
  specified, all branches of the 'origin' remote are scanned.

EOF
    exit 1
fi

function show_version {
    typeset name="$1"
    typeset branch="$2"

    typeset gr_ver=$(git show "${branch}:global-requirements.txt" |
                            grep -i "^${name}[=><]"  |
                            sed -e 's/.*://' -e 's/ .*//')
    typeset c_ver=$(git show "${branch}:upper-constraints.txt" |
                            grep -i "^${name}="  |
                            sed -e 's/.*=//' -e 's/ .*//')

    printf '%-30s %-30s  ===%s\n' $branch $gr_ver $c_ver
}

NAME=$1
shift
BRANCHES="$@"
if [[ -z "$BRANCHES" ]]; then
    BRANCHES=$(git branch -a |
                    grep 'origin/stable' |
                    grep -v HEAD |
                    sed 's|remotes/||' |
                    sort)
    BRANCHES="$BRANCHES master"
fi

for b in $BRANCHES; do
    show_version $NAME $b
done
