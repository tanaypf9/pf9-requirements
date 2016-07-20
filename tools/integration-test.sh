#!/bin/bash

# Usage: integration-test.sh {organization} {project} {path-to-clone}
# Example usage:
#   $ integration-test.sh openstack barbican
#   $ integration-test.sh openstack keystone
#   $ integration-test.sh openstack keystonemiddleware
#   $ integration-test.sh openstack sahara
#   $ integration-test.sh openstack python-keystoneclient \
#       /opt/openstack/python-keystoneclient
set -x
set -e

if [[ $# -lt 2 ]]; then
    echo "Script requires at least two arguments to run."
    echo "Usage: $0 organization project [path-to-clone]"
    exit 1
fi

REPO_ROOT=${REPO_ROOT:-git://git.openstack.org}
org=$1
project=$2

if [[ $# -eq 3 ]] ; then
    projectdir=$3
    clone=0
else
    projectdir="${project}"
    clone=1
fi

workdir="$(pwd)"

if [[ $clone -eq 1 ]] ; then
    tempdir="$(mktemp -d)"
    #trap "rm -rf $tempdir" EXIT

    pushd "${tempdir}"
    git clone "${REPO_ROOT}/${org}/${project}" --depth=1
fi

# specify the use of the upper-constraints.txt from this checkout
export UPPER_CONSTRAINTS_FILE="${workdir}/upper-constraints.txt"
export PATH+=$PATH:${workdir}/.tox/venv/bin

pushd "${workdir}"
    tox -e update -- "${tempdir}/${projectdir}"
popd

pushd "${projectdir}"
    # And now we actually run the tests
    tox -e functional
popd

if [[ $clone -eq 1 ]] ; then
    popd
fi
