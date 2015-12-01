#!/bin/bash

pushd /opt/dogtail
tar xzf /opt/dogtail/dogtail-0.9.0.tar.gz
pushd dogtail-0.9.0
python setup.py install
popd

sed -i 's/os\.getlogin()/"root"/g' /usr/lib/python2.7/site-packages/dogtail/config.py
sed -i 's/os\.environ\['"'USER'"'\]/"root"/g' /usr/lib/python2.7/site-packages/dogtail/config.py
popd
