#!/bin/env python

import sys
from anabot.preprocessor import preprocess

if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(preprocess(*args))
