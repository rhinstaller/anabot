#!/bin/env python2

import libxml2, sys
import time, re
import logging
import signal

logger = logging.getLogger('anabot')
logger.addHandler(logging.NullHandler()) # pylint: disable=no-member

from .default import handle_step
from .default import dump
from . import installation, initial_setup
import pyatspi # pylint: disable=import-error

def run_test(file_path, name="anaconda"):
    """Run anabot with given path to anabot recipe.

    Given file needs to be in "raw" xml schema, which means that it's required
    that this file is already processed by anabot preprocessor.
    See anabot.preprocessor package.
    """
    import dogtail.utils # pylint: disable=import-error
    dogtail.utils.enableA11y()
    import dogtail.config # pylint: disable=import-error
    dogtail.config.config.typingDelay = 0.2
    dogtail.config.config.childrenLimit = 10000
    from dogtail.predicate import GenericPredicate # pylint: disable=import-error
    import dogtail.tree # pylint: disable=import-error
    application = dogtail.tree.root.child(roleName="application", name=name)
    # atspi sometimes has connection issues when asking for parents, so cache
    # them
    application.setCacheMask(pyatspi.cache.PARENT)
    signal.signal(signal.SIGUSR1, lambda x,y: dump(application, '/tmp/dogtail.dump'))
    doc = libxml2.parseFile(file_path)
    handle_step(doc.getRootElement(), application, None)
    doc.freeDoc()

if __name__ == "__main__":
    import os
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":1"

    sys.exit(run_test("examples/autostep.xml"))
