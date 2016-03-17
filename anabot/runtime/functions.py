#!/bin/env python2

import time
import libxml2

import dogtail # pylint: disable=import-error
import dogtail.utils # pylint: disable=import-error
import pyatspi # pylint: disable=import-error
from dogtail.predicate import GenericPredicate # pylint: disable=import-error

from .errors import TimeoutError

_SCREENSHOT_NUM = 0

def inrange(what, border1, border2):
    if border1 == border2:
        return what == border1
    if border1 < border2:
        return border1 <= what and what < border2
    return border2 <= what and what < border1

def visibility(node, value):
    return (value is None) or (bool(value) == node.showing)

def sensitivity(node, value):
    return (value is None) or (bool(value) == node.sensitive)

def waiton(node, predicates, timeout=7, make_screenshot=False, visible=True, sensitive=True, recursive=True):
    "wait unless item shows on the screen"
    count = 0
    if type(predicates) is not list:
        predicates = [predicates]
    while count < timeout:
        count += 1
        for predicate in predicates:
            found = node.findChild(predicate, retry=False, requireResult=False, recursive=recursive)
            if found is not None and visibility(found, visible) and sensitivity(found, sensitive):
                if make_screenshot:
                    screenshot()
                return found
        time.sleep(1)
    screenshot()
    raise TimeoutError("No predicate matches within timeout period")

def waiton_all(node, predicates, timeout=7, make_screenshot=False, visible=True, sensitive=True, recursive=True):
    "wait unless items show on the screen"
    count = 0
    if type(predicates) is not list:
        predicates = [predicates]
    while count < timeout:
        count += 1
        for predicate in predicates:
            found = [x for x in node.findChildren(predicate,
                                                  recursive=recursive) if
                     visibility(x, visible) and sensitivity(x, sensitive)]
            if len(found):
                if make_screenshot:
                    screenshot()
                return found
        time.sleep(1)
    screenshot()
    raise TimeoutError("No predicate matches within timeout period")

def getnodes(parent, node_type=None, node_name=None, timeout=None,
             predicates=None, visible=True, sensitive=True, recursive=True):
    if predicates is None:
        predicates = {}
    if node_type is not None:
        predicates['roleName'] = node_type
    if node_name is not None:
        predicates['name'] = node_name
    if timeout is not None:
        return waiton_all(parent, GenericPredicate(**predicates), timeout,
                          visible=visible, sensitive=sensitive,
                          recursive=recursive)
    return waiton_all(parent, GenericPredicate(**predicates), visible=visible,
                      sensitive=sensitive, recursive=recursive)

def getnode(parent, node_type=None, node_name=None, timeout=None,
            predicates=None, visible=True, sensitive=True, recursive=True):
    return getnodes(parent, node_type, node_name, timeout, predicates, visible, sensitive, recursive)[0]

def getparent(child, node_type=None, node_name=None, predicates=None):
    if predicates is None:
        predicates = {}
    if node_type is not None:
        predicates['roleName'] = node_type
    if node_name is not None:
        predicates['name'] = node_name
    return child.findAncestor(GenericPredicate(**predicates))

def getparents(child, node_type=None, node_name=None, predicates=None):
    parents = []
    while True:
        parent = getparent(child, node_type, node_name, predicates)
        if parent is None:
            return parents
        parents.append(parent)
        child = parent


def findsibling(items, item, distance, criteria=lambda x: True):
    if distance == 0:
        if criteria(item):
            return item
        return None
    elif distance < 0:
        distance *= -1
        items = items[::-1]

    for i in xrange(items.index(item), len(items)):
        if criteria(items[i]):
            distance -= 1
        if distance == 0:
            return items[i]
    return None


def nodematching(node, node_type=None, node_name=None, visible=True,
               sensitive=True):
    if node_type is not None and node.roleName != node_type:
        return False
    if node_name is not None and node.name != node_name:
        return False
    if visible is not None and node.showing != visible:
        return False
    if sensitive is not None and node.sensitive != sensitive:
        return False
    return True


def getsibling(node, vector, node_type=None, node_name=None, visible=True,
               sensitive=True):
    """
    Get n'th (vector is negative or positive number specifying direction and
    distance of search) sibling node that passes given criterie (node_type,
    node_name, visible and sensitive).
    """

    def criteria(node):
        return nodematching(node, node_type, node_name, visible, sensitive)

    nodes = getparent(node).children
    return findsibling(nodes, node, vector, criteria)


def getselected(parent):
    return [child for child in getnodes(parent) if child.selected]

def screenshot(wait=None):
    # DISABLED ATM
    return
    global _SCREENSHOT_NUM
    _SCREENSHOT_NUM += 1
    if wait is not None:
        time.sleep(wait)
    dogtail.utils.screenshot('/var/run/anabot/%02d-screenshot.png' %
                             (_SCREENSHOT_NUM), timeStamp=False)

def get_attr(element, name, default=None):
    try:
        xpath = "./@%s" % name
        return str(element.xpathEval(xpath)[0].getContent())
    except libxml2.xpathError:
        raise Exception("Incorrect xpath expression: '%s'" % xpath)
    except IndexError:
        return default

def hold_key(keyName):
    return key_action(keyName, "press")

def release_key(keyName):
    return key_action(keyName, "release")

def key_action(keyName, action):
    # need to import dogtail.rawinput after display is on, so this is probably
    # the best place for it
    import dogtail.rawinput # pylint: disable=import-error
    actions = {
        "press" : pyatspi.KEY_PRESS,
        "release" : pyatspi.KEY_RELEASE,
        "pressrelease" : pyatspi.KEY_PRESSRELEASE,
    }
    if action not in actions:
        return
    gtk_name = dogtail.rawinput.keyNameAliases[keyName]
    keyCode = dogtail.rawinput.keyNameToKeyCode(gtk_name)
    pyatspi.Registry.generateKeyboardEvent(keyCode, None, actions[action])
    dogtail.rawinput.doTypingDelay()
