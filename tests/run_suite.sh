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
DOGTAIL_DIR=`install_dogtail $ANABOT_DIR/dogtail/dogtail-*.tar.gz`
PYTHONPATH="$DOGTAIL_DIR/lib/python2.7/site-packages/"
pylint --init-hook="sys.path.append('$DOGTAIL_DIR/lib/python2.7/site-packages/')" anabot || SCORE=$[SCORE+1]

rm -rf -- "$DOGTAIL_DIR"
popd &> /dev/null

exit $SCORE
