#!/usr/bin/env bash

if [ -z "$VIRTUAL_ENV" ] ; then
    tox -evenv --notest
    . .tox/venv/bin/activate
fi

set -x

python tools/find-open-constratints-reviews.py --query 'is:open topic:feature/add-constraints-support age:1d' | while read project change_nr
do
    bash tools/fixup-constratints.sh "$project" "$change_nr" </dev/null
done
