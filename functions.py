#!/bin/env python2

import os, time

class TimeoutError(Exception):
    pass

def waiton(node, predicates, timeout=7, make_screenshot=True):
    "wait unless items show on the screen"
    count = 0
    if type(predicates) is not list:
        predicates = [predicates]
    while count < timeout:
        count += 1
        for predicate in predicates:
            found = node.findChild(predicate, retry=False, requireResult=False)
            if found is not None and found.showing and found.sensitive:
                if make_screenshot:
                    screenshot()
                return found
        time.sleep(1)
    screenshot()
    raise TimeoutError("None predicate matches within timeout period")

def screenshot(wait=None):
    if wait is not None:
        time.sleep(wait)
    os.system("/dogtail/screenshot dogtail-anaconda.png 1")
