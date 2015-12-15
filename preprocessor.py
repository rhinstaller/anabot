#!/bin/env python

import sys
from anabot.preprocessor import preprocess

import logging

if __name__ == "__main__":
    logger = logging.getLogger("anabot.preprocessor")
    logger.addHandler(logging.StreamHandler(sys.stderr))
    args = sys.argv[1:]
    sys.exit(preprocess(*args))
