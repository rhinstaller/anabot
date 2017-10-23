#!/bin/bash

PYTHON=`which /usr/libexec/platform-python python3 python2 2> /dev/null | head -n 1`
exec $PYTHON "$@"
