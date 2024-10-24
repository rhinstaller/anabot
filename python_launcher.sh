#!/bin/bash

# The sleep has been moved from the unit file. It's necessary (at least on <= RHEL-9)
# to work around issues with dogtail not being able to properly connect to the
# ATK D-Bus.
sleep 30
PYTHON=`which /usr/libexec/platform-python python3 python2 2> /dev/null | head -n 1`
exec $PYTHON "$@"
