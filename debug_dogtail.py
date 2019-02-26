#!/usr/bin/python2 -i

import logging
logger = logging.getLogger("anabot")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

import sys
import os

def list_dirs(path):
    return [
        os.path.join(path, x)
        for x in os.listdir(path)
        if os.path.isdir(os.path.join(path, x))
    ]

os.environ["DISPLAY"] = ":1"

# Add dogtail import path
for d in list_dirs('dogtail'):
    sys.path.append(d)
# Add teres import path
sys.path.append('teres')

try:
    app_name = sys.argv[1]
except IndexError:
    app_name = "anaconda"

import dogtail
import dogtail.config
dogtail.config.config.checkForA11y = False
dogtail.config.config.childrenLimit = 10000
from dogtail.predicate import GenericPredicate
import dogtail.tree

app_node = dogtail.tree.root.child(roleName="application", name=app_name)

from anabot.runtime.functions import waiton, waiton_all, getnode, getnode_scroll, getnodes, getparent, getparents, getsibling, hold_key, release_key, dump, scrollto
from anabot.runtime.translate import set_languages, tr
from anabot.runtime.installation.hub.keyboard.layouts import layout_name
set_languages(['cs_CZ', 'cs'])
