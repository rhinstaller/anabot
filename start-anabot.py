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


teres_logger = logging.getLogger("teres")
teres_logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("/var/log/anabot-teres.log"))
teres_stdout_handler = logging.StreamHandler(sys.stdout)
teres_stdout_handler.setFormatter(logging.Formatter("TERES: %(message)s"))
teres_logger.addHandler(teres_stdout_handler)
if os.environ.get('TERES_PATH'):
    sys.path.append(os.environ.get('TERES_PATH'))
import teres
import teres.handlers
reporter = teres.Reporter.get_reporter()
test_log_handler = logging.FileHandler("/var/log/anabot-test.log")
reporter.add_handler(teres.handlers.LoggingHandler('anabot.test',
                                                   test_log_handler,
                                                   dest=None))

from anabot.exceptions import UnrelatedException
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
        except UnrelatedException as e:
            logger.debug("Module reports, that it's not related for current environment")

os.environ["DISPLAY"] = ":1"

from anabot.runtime import run_test
from anabot.preprocessor import preprocess

preprocess("/var/run/anabot/raw-recipe.xml", "/var/run/anabot/final-recipe.xml")
run_test("/var/run/anabot/final-recipe.xml")
