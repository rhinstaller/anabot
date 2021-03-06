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
from anabot.runtime.hooks import run_prehooks, run_posthooks

def run_test(file_path, appname="anaconda", children_required=0):
    """Run anabot with given path to anabot recipe.

    Given file needs to be in "raw" xml schema, which means that it's required
    that this file is already processed by anabot preprocessor.
    See anabot.preprocessor package.
    """
    import dogtail.config # pylint: disable=import-error
    dogtail.config.config.checkForA11y = False
    dogtail.config.config.typingDelay = 0.2
    dogtail.config.config.childrenLimit = 10000
    from dogtail.predicate import GenericPredicate # pylint: disable=import-error
    import dogtail.tree # pylint: disable=import-error
    application = dogtail.tree.root.child(roleName="application", name=appname)
    # atspi sometimes has connection issues when asking for parents, so cache
    # them
    application.setCacheMask(pyatspi.cache.PARENT)
    signal.signal(signal.SIGUSR1, lambda x,y: dump(application, '/tmp/dogtail.dump'))
    doc = libxml2.parseFile(file_path)
    run_prehooks()
    handle_step(doc.getRootElement(), application, None)
    run_posthooks()
    doc.freeDoc()

