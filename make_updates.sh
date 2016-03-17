#!/bin/bash

DESTINATION=${1:-../updates.tar.gz}
TMPDIR=`mktemp -d`
mkdir $TMPDIR/opt
cp -r * $TMPDIR/opt
mv $TMPDIR/opt/etc $TMPDIR
MODULES_DIR=$TMPDIR/opt/modules
for HOOK_TYPE in preexec pre post-nochroot post; do
    HOOK_DEST=$TMPDIR/opt/anabot-hooks/$HOOK_TYPE
    mkdir -p $HOOK_DEST
    for MODULE in `ls $MODULES_DIR`; do
	for HOOK in $MODULES_DIR/$MODULE/*-$HOOK_TYPE.hook; do
	    if [ -e $HOOK ]; then
		PRIO=`basename $HOOK | egrep -o '^[0-9]{2}'`
		cp $HOOK $HOOK_DEST/$PRIO-$MODULE
	    fi
	done
    done
done
mv $MODULES_DIR $TMPDIR/opt/anabot-modules

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR
