#!/bin/env python

import sys

def preprocess(input_path = '-', output_path = '-'):
    if input_path == '-':
        input_fo = sys.stdin
    else:
        input_fo = open(input_path)
    if output_path == '-':
        output_fo = sys.stdout
    else:
        output_fo = open(output_path, 'w')
    # no preprocessing at the moment
    output_fo.write(input_fo.read())

if __name__ == "__main__":
    sys.exit(preprocess(*sys.argv[1:]))
