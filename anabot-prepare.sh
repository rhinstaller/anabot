#!/usr/bin/bash

# Deploy non-git (in bundled directory) content in the installer environment
cp -r /opt/bundled-bin/$(uname -m)/* /
[ -d /opt/bundled-bin/noarch ] && cp -r /opt/bundled-bin/noarch/* /

# Create a wrapper for gnome-kiosk to run it with introspection enabled
# (which means with '--unsafe-mode' parameter)
if [ ! -f /bin/gnome-kiosk_ ]; then
    echo "Creating wrapper script for /bin/gnome-kiosk to run in unsafe mode"
    mv /bin/gnome-kiosk /bin/gnome-kiosk_
    cat > /bin/gnome-kiosk <<- "EOF"
#!/usr/bin/bash
/bin/gnome-kiosk_ "$@" --unsafe-mode
EOF
    chmod +x /bin/gnome-kiosk
fi

# Create Anaconda desktop file (needed for dogtail to find the window)
cat > /usr/share/applications/anaconda.desktop << EOF
[Desktop Entry]

Name=Anaconda
Comment=Graphical system installer
Terminal=false
Type=Application
Categories=System;
Exec=anaconda
NoDisplay=true
EOF
