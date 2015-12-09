#!/bin/env python2

from test import run_test
from preprocessor import preprocess
import os, sys
os.environ["DISPLAY"] = ":1"

preprocess("/var/run/anabot/raw-recipe.xml", "/var/run/anabot/final-recipe.xml")
run_test("/var/run/anabot/final-recipe.xml")
