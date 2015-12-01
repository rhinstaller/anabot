#!/bin/bash

UPDATES=`sed -re 's/.*(inst\.)?updates=([^[:space:]]+).*/\2/' /proc/cmdline`

pushd /
curl $UPDATES | tar xzf -
popd
