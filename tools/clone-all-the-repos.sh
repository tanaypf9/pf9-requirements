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

case "$1" in
--help)
    echo "$0 [glob]"
    echo ""
    echo "glob is a simple rexgex for project to consider"
    exit 0
;;
esac

for prj in $(ssh review.openstack.org -qt gerrit ls-projects) ; do
    if [[ "$prj" =~ "$1" ]] ; then
        echo Prociessing project: $prj
    else
        echo Skipping project: $prj
    fi

    d=$(dirname $prj)
    mkdir -p $d
    if [ -d $prj ] ; then
        (
        cd $prj
        git remote update
        )
    else
        (cd $d; git clone git://git.openstack.org/$prj)
        (cd $prj; git review -s)
    fi
done
