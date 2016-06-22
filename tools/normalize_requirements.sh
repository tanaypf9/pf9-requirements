#! /bin/bash

set -ex

tmpfile=`mktemp`
cmds/normalize global-requirements.txt >  tmpfile
mv tmpfile global-requirements.txt
