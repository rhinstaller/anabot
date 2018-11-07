#!/bin/bash

DESTINATION=${1:-../updates.tar.gz}
TMPDIR=`mktemp -d`
mkdir $TMPDIR/opt
cp -r * $TMPDIR/opt
mv $TMPDIR/opt/etc $TMPDIR
cat > $TMPDIR/opt/anabot.ini <<EOF
[DEFAULT]
var_beaker_hub_hostname=${BEAKER_HUB_HOSTNAME}
EOF

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR
