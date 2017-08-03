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

function usage()
{
    (
    if [ -n "$1" ] ; then
        echo $0 $1
    fi
    echo $0 '-p [project] -t [topic] -c [change] -s [style]'
    echo ' project: The directory for the openstack project'
    echo ' topic  : The topic as passed to git review'
    echo ' change : The change that the no-op chgnae depends on'
    echo ' style  : the style of change [doc|python|releasenotes]'
    ) >&2
    exit 1
}

project=''
topic=''
change=''
style=''
verbose=0

while getopts vp:t:c:s: opt ; do
    case $opt in
    p)
        project=${OPTARG/=}
    ;;
    t)
        topic=${OPTARG/=}
    ;;
    c)
        change=${OPTARG/=}
    ;;
    s)
        style=${OPTARG/=}
    ;;
    v)
        verbose=$((verbose + 1))
    ;;
    \?)
        usage
    ;;
    esac
done

if [ -z "$project" ] ; then
    usage 'project missing!'
fi

if [ -z "$topic" ] ; then
    usage 'topic missing!'
fi
# FIXME(tonyb): Validate topic is sensible. Which I think just means no
#               whitspace.

if [ -z "$style" ] ; then
    usage 'style missing!'
elif [[ ! 'releasenotes doc python' =~ "$style" ]] ; then
    usage "style $style invalid"
fi

if [ $verbose -ge 1 ] ; then
    printf '%-10s: %s\n' 'Project' "$project"
    printf '%-10s: %s\n' 'Topic' "$topic"
    printf '%-10s: %s\n' 'Change' "$change"
    printf '%-10s: %s\n' 'Style' "$style"
    printf '%-10s: %s\n' 'Verbosity' "$verbose"
fi

if [ $verbose -ge 2 ] ; then
    set -x
fi

exit 0
cd $project

set -e
# FIXME(tonyb): Save the current branch
start_branch=$(git rev-parse --symbolic --abbrev-ref HEAD)
if [ "$start_branch" == "$topic" ] ; then
    echo $0 Current git branch is the same as topic aborting >&2
    exit 1
fi

# NOTE(tonyb): git diff exits with 0 if the tree is clean
if ! git diff --exit-code -s ; then
    echo $0 Current working tree is dirty aborting >&2
    exit 1
fi

git branch -D ${topic} || true
# NOTE(tonyb): We don't really need to switch branches we could do it all in
#              the current branch but this is easier.
git checkout -b ${topic} -t origin/master

case "$style" in
releasenotes|doc)
    file="${style}/source/index.rst"
    [ "$verbose" -ge 3 ] && git diff
    echo -e '\n\n.. # no-op test' >> $file
    git add $file
;;
python)
    # TODO(tonyb): work out a 99% safe way to modify python code
    echo $0 python syle change isn\'t finished
    exit 1
    file=$(find * -type f -name __init__.py | sort | head -n 1)
    echo -e '\n\n# no-op test' >> ${file}
    [ "$verbose" -ge 3 ] && git diff
    git add $file
;;
esac

commit_msg="WiP: Do not merge - $topic"
if [ -n "$change" ] ; then
    commit_msg+="

Depends-On: $change"
fi
git commit -m "$commit_msg"
git review -t ${topic}
# TODO(tonyb): Check for vote-a-tron and -W the change if it's available

# FIXME(tonyb): Move this to an exit trap handler?
git checkout $start_branch
git branch -D ${topic}
