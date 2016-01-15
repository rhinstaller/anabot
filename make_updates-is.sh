#!/bin/bash

DESTINATION=${1:-../updates-is.tar.gz}
TMPDIR=`mktemp -d`
mkdir $TMPDIR/opt
cp -r * $TMPDIR/opt
# mv $TMPDIR/opt/etc $TMPDIR

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR
