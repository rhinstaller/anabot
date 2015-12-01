#!/usr/bin/env python2

import os
os.environ["DISPLAY"] = ":1"
import dogtail.utils
dogtail.utils.enableA11y()
from dogtail.predicate import GenericPredicate
import dogtail.tree
dogtail.tree.root.dump(fileName='/tmp/dogtail.dump')
