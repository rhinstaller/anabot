#!/bin/bash

install_dogtail() {
    pushd `mktemp -d` &> /dev/null
    local DOGTAIL_DIR=`pwd`
    tar xzf $1
    pushd dogtail* &> /dev/null
    python setup.py install --prefix $DOGTAIL_DIR > /dev/null
    popd &> /dev/null
    rm -rf dogtail*
    echo $DOGTAIL_DIR
    popd &> /dev/null
}

uninstall_dogtail() {
    rm -rf -- $1
}

SCORE=0

pushd .. &> /dev/null
ANABOT_DIR=`pwd`
#DOGTAIL_DIR=`install_dogtail $ANABOT_DIR/dogtail/dogtail-*.tar.gz`
# pylint's return code is bit-ORed value of statuses. See pylint manpage.
# 3 means: 1 - fatal message + 2 - error message
if ! [ -e teres/.git ]; then
    # workaround jenkins git clone behaviour
    git submodule update --init teres
fi
pylint --init-hook="import sys; sys.path.append('./teres/')" anabot; PYLINT_RETCODE=$?
test $[PYLINT_RETCODE & 3] -ne 0 && SCORE=$[SCORE+1]

#rm -rf -- "$DOGTAIL_DIR"
popd &> /dev/null

exit $SCORE
