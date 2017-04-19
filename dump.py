#!/usr/bin/env python2

import os
import sys
my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(my_path, 'lib/python2.7/site-packages'))

if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":1"
print 'using DISPLAY="%s"' % os.environ['DISPLAY']

import dogtail.utils
import dogtail.config
dogtail.utils.enableA11y()
dogtail.config.config.childrenLimit = 10000
import dogtail.tree
dogtail.tree.root.dump(fileName='/tmp/dogtail.dump')
