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
