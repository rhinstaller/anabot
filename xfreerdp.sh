#!/usr/bin/bash

while sleep 1; do
     pidof gnome-kiosk_ && break
done
# Connect only a few seconds after the Anaconda window appears. If the virtual
# monitor created by the connection is added within a few hundred ms after the
# window is mapped, the window can stay 1x1 forever (INSTALLER-4905).
for ((i = 0; i < 300; i++)); do
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus dbus-send --session \
        --print-reply --dest=org.gnome.Shell.Introspect /org/gnome/Shell/Introspect \
        org.gnome.Shell.Introspect.GetWindows 2>/dev/null \
        | grep -q 'string "anaconda.desktop"' && break
    sleep 1
done
sleep 3
while :; do
    /usr/bin/xvfb-run -a -e /tmp/xvfb-run-err.log -s "-screen 0 1024x768x24" /usr/bin/xfreerdp /u:username /p:password /v:localhost /cert:ignore /size:1024x768
    sleep 1
done
