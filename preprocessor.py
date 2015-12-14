#!/bin/env python

import sys
from anabot.preprocessor import preprocess

if __name__ == "__main__":
    args = sys.argv[1:]
    args.append(True) # debug
    sys.exit(preprocess(*args))
