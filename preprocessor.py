#!/bin/env python

# usage:
# preprocessor.py [input [output [appname [varname=value [varname2=value2 ...]]]]]
# if no params are given reads stdin outputs stdout and use installation appname
# input / output can be set to '-' for stdin / stdout
# appname is preprocessor profile
# varname=value is used to set internal anabot variables 
#  (useful for dynamically setting usernames/hostnames/passwords in recipe file)

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
