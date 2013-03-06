#!/bin/bash

GIT_DIR=${GIT_DIR-~/git/openstack}
FETCH_REMOTE=${FETCH_REMOTE-}
REMOTE_BRANCH=${REMOTE_BRANCH-gerrit/master}
PROJECTS=${PROJECTS-"nova glance keystone cinder quantum horizon swift heat ceilometer oslo-incubator python-novaclient python-glanceclient python-keystoneclient python-cinderclient python-quantumclient python-swiftclient"}

fetch() {
    for p in $PROJECTS; do
        cd $GIT_DIR/$p
        git fetch gerrit
    done
}

concat() {
    path=$1; shift

    for p in $PROJECTS; do
        cd $GIT_DIR/$p
        git cat-file -p $REMOTE_BRANCH:$path
    done | tr A-Z a-z| sed 's/#.*$//; s/ *$//; /^ *$/d' | sort | uniq
}

file_to_regexp() {
    file=$1; shift

    echo -n "\("
    xargs -i echo -n "^{}$\|" < $file
    echo -n "^$\)"
}

[ -n "$FETCH_REMOTE" ] && fetch

concat tools/pip-requires > $GIT_DIR/requirements/tools/pip-requires

exclude=$(file_to_regexp $GIT_DIR/requirements/tools/pip-requires)
concat tools/test-requires | grep -v "$exclude" > $GIT_DIR/requirements/tools/test-requires
