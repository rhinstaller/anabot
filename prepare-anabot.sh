#!/bin/bash

while [ ! -e /tmp/.X11-unix/X1 ]; do
    echo "Waiting for X server to start"
    sleep 5
done
sleep 5

pushd /opt/dogtail
tar xzf /opt/dogtail/dogtail-0.9.1.tar.gz
pushd dogtail-0.9.1
python setup.py install --prefix /opt/
popd

sed -i 's/os\.getlogin()/"root"/g' /opt/lib/python2.7/site-packages/dogtail/config.py
sed -i 's/os\.environ\['"'USER'"'\]/"root"/g' /opt/lib/python2.7/site-packages/dogtail/config.py
popd

mkdir -p /var/run/anabot 2> /dev/null

RECIPE_URL=`awk 'BEGIN {RS=" |\n"; FS="="} $1 == "anabot" {print $2}' /proc/cmdline`
if [ "$RECIPE_URL" ]; then
    curl -k $RECIPE_URL > /var/run/anabot/raw-recipe.xml
else
    cp /opt/examples/minimal.xml /var/run/anabot/raw-recipe.xml
fi
