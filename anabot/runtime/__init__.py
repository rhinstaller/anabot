#!/bin/env python2

import libxml2, sys
import time, re
import logging

logger = logging.getLogger('anabot')
logger.addHandler(logging.NullHandler()) # pylint: disable=no-member

from .default import handle_step
from . import installation
import pyatspi # pylint: disable=import-error

def run_test(file_path):
    """Run anabot with given path to anabot recipe.

    Given file needs to be in "raw" xml schema, which means that it's required
    that this file is already processed by anabot preprocessor.
    See anabot.preprocessor package.
    """
    import dogtail.utils # pylint: disable=import-error
    dogtail.utils.enableA11y()
    import dogtail.config # pylint: disable=import-error
    dogtail.config.config.typingDelay = 0.2
    dogtail.config.config.logDebugToFile = False
    dogtail.config.config.logDebugToStdOut = False
    from dogtail.predicate import GenericPredicate # pylint: disable=import-error
    import dogtail.tree # pylint: disable=import-error
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
