#!/usr/libexec/platform-python -i

import sys
import os
import logging

logger = logging.getLogger("anabot")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# this should setup paths for imports
from anabot import paths

os.environ["DISPLAY"] = ":1"
with open("/run/anabot/session_type", "r") as st:
    if st.read() == "wayland":
        os.environ["XDG_RUNTIME_DIR"] = "/run/user/0"
        os.environ["WAYLAND_DISPLAY"] = "wl-sysinstall-0"
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/run/user/0/bus"
        os.environ["XDG_SESSION_TYPE"] = "wayland"
        from subprocess import call
        if call("systemctl --user is-active gnome-ponytail-daemon", shell="True") > 0:
            print("gnome-ponytail-daemon user service not running, going to start it...")
            if call("systemctl --user start gnome-ponytail-daemon", shell="True") > 0:
                print("Couldn't start gnome-ponytail-daemon.")
                sys.exit(1)

try:
    app_name = sys.argv[1]
except IndexError:
    app_name = "anaconda"

import dogtail
import dogtail.config
dogtail.config.config.checkForA11y = False
dogtail.config.config.childrenLimit = 10000
import dogtail.tree

app_node = dogtail.tree.root.child(roleName="application", name=app_name)

from anabot.runtime.functions import getnode, getnode_scroll, getnodes, getparent, getparents, getsibling, hold_key, release_key, dump, scrollto
from anabot.runtime.translate import set_languages, tr
set_languages(['cs_CZ', 'cs'])
