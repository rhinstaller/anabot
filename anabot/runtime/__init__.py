#!/bin/env python2

if __name__ == "__main__":
    import os, sys
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":1"
    from .run_test import run_test

    sys.exit(run_test("examples/autostep.xml"))
