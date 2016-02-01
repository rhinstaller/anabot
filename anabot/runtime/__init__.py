#!/bin/env python2

import libxml2, sys
import time, re
import logging

logger = logging.getLogger('anabot')
logger.addHandler(logging.NullHandler())

from .default import handle_step
from . import installation
import pyatspi

def run_test(file_path):
    import dogtail.utils
    dogtail.utils.enableA11y()
    import dogtail.config
    dogtail.config.config.typingDelay = 0.2
    from dogtail.predicate import GenericPredicate
    import dogtail.tree
    anaconda = dogtail.tree.root.child(roleName="application", name="anaconda")
    # atspi sometimes has connection issues when asking for parents, so cache
    # them
    anaconda.setCacheMask(pyatspi.cache.PARENT)
    doc = libxml2.parseFile(file_path)
    handle_step(doc.getRootElement(), anaconda, None)
    doc.freeDoc()

if __name__ == "__main__":
    import os
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":1"

    sys.exit(run_test("examples/autostep.xml"))
