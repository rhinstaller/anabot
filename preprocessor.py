#!/bin/env python

import sys
from anabot.preprocessor import preprocess
from anabot.variables import set_variable

import logging

if __name__ == "__main__":
    logger = logging.getLogger("anabot.preprocessor")
    logger.addHandler(logging.StreamHandler(sys.stderr))
    preprocessor_args = sys.argv[1:4]
    for arg in sys.argv[4:]:
        name, value = arg.split('=', 1)
        set_variable(name, value)
    sys.exit(preprocess(*preprocessor_args))
