#!/bin/bash

DESTINATION=${1:-../updates.tar.gz}
TMPDIR=`mktemp -d`
mkdir $TMPDIR/opt
cp -r * $TMPDIR/opt
mv $TMPDIR/opt/etc $TMPDIR
cat > $TMPDIR/opt/anabot.ini <<EOF
[DEFAULT]
var_beaker_hub_hostname=${BEAKER_HUB_HOSTNAME}
var_ca_certificate_url=${CA_CERTIFICATE_URL}
EOF

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR
