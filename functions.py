#!/bin/env python2

import os, time
import libxml2

class TimeoutError(Exception):
    pass

def waiton(node, predicates, timeout=7, make_screenshot=True):
    "wait unless item shows on the screen"
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

def waiton_all(node, predicates, timeout=7, make_screenshot=True):
    "wait unless items show on the screen"
    count = 0
    if type(predicates) is not list:
        predicates = [predicates]
    while count < timeout:
        count += 1
        for predicate in predicates:
            found = [ x for x in node.findChildren(predicate)
                      if x.showing and x.sensitive ]
            if len(found):
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

def get_attr(element, name, default=None):
    try:
        xpath = "./@%s" % name
        return str(element.xpathEval(xpath)[0].getContent())
    except libxml2.xpathError:
        raise Exception("Incorrect xpath expression: '%s'" % xpath)
    except IndexError:
        if default is None:
            raise KeyError("No attribute named '%s'" % name)
        return default
