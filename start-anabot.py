#!/bin/env python2

import os, sys, shutil
from importlib import import_module

import logging
from logging.handlers import SysLogHandler

logger = logging.getLogger("anabot")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("/var/log/anabot.log"))
syslog = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL3)
syslog.setFormatter(logging.Formatter("anabot: %(message)s"))
# virtio console - useful for debugging
VIRTIO_CONSOLE = '/dev/virtio-ports/com.redhat.anabot.0'
if os.path.exists(VIRTIO_CONSOLE):
    logger.addHandler(logging.FileHandler(VIRTIO_CONSOLE))
logger.addHandler(syslog)

modules_path = os.environ.get('ANABOT_MODULES')
if modules_path is not None and os.path.isdir(modules_path):
    sys.path.append(modules_path)
    for module_name in sorted(os.listdir(modules_path)):
        try:
            logger.debug("Importing anabot module: %s", module_name)
            module = import_module(module_name)
            logger.debug("Imported anabot module: %s", module_name)
        except ImportError:
            logger.debug("Import failed for anabot module: %s", module_name)
            pass

os.environ["DISPLAY"] = ":1"

from anabot.runtime import run_test
from anabot.preprocessor import preprocess

preprocess("/var/run/anabot/raw-recipe.xml", "/var/run/anabot/final-recipe.xml")
run_test("/var/run/anabot/final-recipe.xml")
