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
    from gi import require_version
    require_version('Gdk', '3.0')
    from gi.repository import Gdk # pylint: disable=no-name-in-module

    # Workaround for a situation when a default display is missing for some reason.
    # It is not clear at this point whether this really is a workaround and it should be
    # fixed (potentially) in dogtail.
    if Gdk.Display.get_default() is None:
        import os
        logger.debug("Default GDK display not found! Opening the display explicitly.")
        if "WAYLAND_DISPLAY" in os.environ.keys():
            display_name = os.environ["WAYLAND_DISPLAY"]
        elif "DISPLAY" in os.environ.keys():
            display_name = os.environ["DISPLAY"]
        else:
            logger.error("Can't find a display name to open explicitly, Anabot run may fail!")
            # Let's assume Anaconda running on Wayland, as this is likely the only problematic
            # configuration anyway.
            display_name = "wl-sysinstall-0"
        Gdk.Display.open(display_name)
        logger.debug(f"Explicitly opened display: '{Gdk.Display.get_default().get_name()}'")

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

