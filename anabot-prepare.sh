#!/usr/bin/bash

# Deploy non-git (in bundled directory) content in the installer environment
cp -r /opt/bundled-bin/$(uname -m)/* /
[ -d /opt/bundled-bin/noarch ] && cp -r /opt/bundled-bin/noarch/* /
