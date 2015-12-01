#!/bin/bash

DESTINATION=${1:-../updates.tar.gz}
tar --transform='s|^|opt/|' --exclude=.git -czf $DESTINATION .
