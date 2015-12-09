#!/bin/env python2

from test import run_test
from preprocessor import preprocess
import os, sys, shutil

import logging
logger = logging.getLogger("anabot")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("/var/log/anabot.log"))

os.environ["DISPLAY"] = ":1"

preprocess("/var/run/anabot/raw-recipe.xml", "/var/run/anabot/final-recipe.xml")
run_test("/var/run/anabot/final-recipe.xml")

shutil.copyfile("/var/log/anabot.log", "/mnt/sysimage/root/anabot.log")
