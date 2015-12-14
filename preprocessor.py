#!/bin/env python

import sys
from anabot.preprocessor import preprocess

if __name__ == "__main__":
    sys.exit(preprocess(*sys.argv[1:]))
