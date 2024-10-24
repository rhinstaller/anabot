#!/usr/bin/bash

while sleep 1; do
     pidof gnome-kiosk_ && break
done
sleep 2
while :; do
    /usr/bin/xvfb-run -a -e /tmp/xvfb-run-err.log -s "-screen 0 1024x768x24" /usr/bin/xfreerdp /u:username /p:password /v:localhost /cert:ignore /size:1024x768
    sleep 1
done
