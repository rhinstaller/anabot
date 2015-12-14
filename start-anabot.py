#!/bin/env python2

from anabot import run_test
from anabot.preprocessor import preprocess
import os, sys, shutil

import logging
from logging.handlers import SysLogHandler
logger = logging.getLogger("anabot")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("/var/log/anabot.log"))
syslog = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL3)
syslog.setFormatter(logging.Formatter("anabot: %(message)s"))
logger.addHandler(syslog)

os.environ["DISPLAY"] = ":1"

preprocess("/var/run/anabot/raw-recipe.xml", "/var/run/anabot/final-recipe.xml")
run_test("/var/run/anabot/final-recipe.xml")

shutil.copyfile("/var/log/anabot.log", "/mnt/sysimage/root/anabot.log")
