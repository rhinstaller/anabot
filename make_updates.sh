#!/bin/bash

DESTINATION=${1:-../updates.tar.gz}
TMPDIR=`mktemp -d`
mkdir $TMPDIR/opt
cp -r * $TMPDIR/opt
mv $TMPDIR/opt/etc $TMPDIR
mv $TMPDIR/opt/lib64 $TMPDIR

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR
