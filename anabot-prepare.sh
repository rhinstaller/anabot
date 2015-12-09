#!/bin/bash

while [ ! -e /tmp/.X11-unix/X1 ]; do
    echo "Waiting for X server to start"
    sleep 5
done
sleep 5

pushd /opt/dogtail
tar xzf /opt/dogtail/dogtail-0.9.0.tar.gz
pushd dogtail-0.9.0
python setup.py install
popd

sed -i 's/os\.getlogin()/"root"/g' /usr/lib/python2.7/site-packages/dogtail/config.py
sed -i 's/os\.environ\['"'USER'"'\]/"root"/g' /usr/lib/python2.7/site-packages/dogtail/config.py
popd

mkdir -p /var/run/anabot 2> /dev/null

cp /opt/examples/autostep.xml /var/run/anabot/raw-recipe.xml
