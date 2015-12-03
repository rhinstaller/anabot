#!/usr/bin/env python2

import os
os.environ["DISPLAY"] = ":1"
import dogtail.utils
import dogtail.config
dogtail.utils.enableA11y()
dogtail.config.config.childrenLimit = 10000
import dogtail.tree
dogtail.tree.root.dump(fileName='/tmp/dogtail.dump')
