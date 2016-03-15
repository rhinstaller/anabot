#!/bin/bash

DESTINATION=${1:-../updates.tar.gz}
TMPDIR=`mktemp -d`
mkdir $TMPDIR/opt
cp -r * $TMPDIR/opt
mv $TMPDIR/opt/etc $TMPDIR
MODULES_DIR=$TMPDIR/opt/modules
for HOOK_TYPE in pre postnochroot post; do
    HOOK_DEST=$TMPDIR/opt/anabot-hooks/$HOOK_TYPE
    mkdir -p $HOOK_DEST
    for MODULE in `ls $MODULES_DIR`; do
	if [ -e $MODULES_DIR/$MODULE/$HOOK_TYPE ]; then
	    cp $MODULES_DIR/$MODULE/$HOOK_TYPE $HOOK_DEST/$MODULE
	fi
    done
done

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR
