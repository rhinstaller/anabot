#!/bin/bash

# create image for beaker initial-setup tests
# it skips systemd units etc.


DESTINATION=${1:-../anabot-is.tar.gz}
TMPDIR=`mktemp -d`
if [ -z "$TMPDIR" ]; then
    echo "Empty string for TMPDIR !!!!" >&2
    exit 2
fi
if ! [ -d "$TMPDIR" ]; then
    echo "Directory '$TMPDIR' does not exist" >&2
    exit 2
fi
cp -r -- * $TMPDIR/

tar -C $TMPDIR -czf $DESTINATION .

rm -rf -- $TMPDIR

