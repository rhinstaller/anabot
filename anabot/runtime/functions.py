#!/bin/env python2

import time
import os, sys
import libxml2
import hashlib
import functools
import copy
import datetime

import dogtail # pylint: disable=import-error
import dogtail.utils # pylint: disable=import-error
import dogtail.dump # pylint: disable=import-error
import pyatspi # pylint: disable=import-error
from dogtail.predicate import GenericPredicate # pylint: disable=import-error
from anabot.paths import screenshot_executable

from .errors import NonexistentError, TimeoutError

import logging
logger = logging.getLogger('anabot')

import teres
import teres.bkr_handlers
reporter = teres.Reporter.get_reporter()

_DEFAULT_TIMEOUT = 7
_DEFAULT_INTERVAL = 0.5

_SCREENSHOT_NUM = 0
_SCREENSHOT_SUM = None
_SCREENSHOT_PROGRESS_SUM = None

class AnabotPredicate(GenericPredicate):
    def __init__(self, node_type=None, name=None, **kwargs):
        self.attrs = copy.deepcopy(kwargs)
        if 'visible' in self.attrs:
            reporter.log_info(
                'Predicate deprecation warning: tranlating visible to showing'
            )
            self.attrs['showing'] = self.attrs['visible']
            del self.attrs['visible']
        super(AnabotPredicate, self).__init__(name, node_type)

    def _genCompareFunc(self):
        orig_satisfiedByNode = super(AnabotPredicate, self)._genCompareFunc()
        def satisfiedByNode(node):
            if not orig_satisfiedByNode(node):
                return False
            for attr, value in self.attrs.items():
                if value is None:
                    # don't care about this attr
                    continue
                if getattr(node, attr, False) != value:
                    return False
            return True
        return satisfiedByNode

    def __repr__(self):
        return '<AnabotPredicate %r>' % self.__dict__

FIND_FAIL_MSG = "Couldn't find result for: %(func)s with args: %(args)s kwargs: %(kwargs)s"
def timed_retries(seconds, exception, func, *args, **kwargs):
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=seconds)
    while datetime.datetime.now() < end_time:
        try:
            result = func(*args, **kwargs)
            if result:
                return result
        except dogtail.tree.SearchError:
            reporter.log_debug(
                FIND_FAIL_MSG % {
                    'func' : func,
                    'args' : args,
                    'kwargs' : kwargs,
                }
            )
        time.sleep(_DEFAULT_INTERVAL)
    raise exception

def attempted_retries(attempts, exception, func, *args, **kwargs):
    for i in range(attempts):
        try:
            result = func(*args, **kwargs)
            if result:
                return result
        except dogtail.tree.SearchError:
            log_screenshot(progress_only=True)
            reporter.log_debug(
                FIND_FAIL_MSG % {
                    'func' : func,
                    'args' : args,
                    'kwargs' : kwargs,
                }
            )
        time.sleep(_DEFAULT_INTERVAL)
    raise exception

def is_alive(node):
    timeout, interval = _DEFAULT_TIMEOUT, _DEFAULT_INTERVAL
    while node.dead and timeout > 0:
        time.sleep(interval)
        timeout -= interval
    # just 'not node.dead' is not sufficient because of the way dogtail behaves
    return not node.dead or node.showing

def _alive(node):
    if not is_alive(node):
        raise NonexistentError("Queried node '%s' is dead and not showing." % node)
    return node

def _check_existence(func):
    @functools.wraps(func)
    def wrapper(node, *args, **kwargs):
        if not is_alive(node):
            raise NonexistentError("Node '%s' queried in function '%s' is dead "
                                   "and not showing." % (node, func.__name__))
        return func(node, *args, **kwargs)
    return wrapper

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

def wait_until_disappear(node, predicate, timeout=_DEFAULT_TIMEOUT,
                         make_screenshot=False, recursive=True):
    count = 0
    while count < timeout:
        count += 1
        found = node.findChild(predicate, retry=False, requireResult=False, recursive=recursive)
        if found is None or visibility(found, False):
            if make_screenshot:
                log_screenshot()
            return
        time.sleep(1)
    log_screenshot(progress_only=True)
    raise TimeoutError("Queried element still visible.", locals())

def disappeared(parent, node_type=None, node_name=None,
                timeout=_DEFAULT_TIMEOUT, recursive=True):
    predicate = GenericPredicate(roleName=node_type, name=node_name)
    try:
        wait_until_disappear(parent, predicate, timeout, recursive=recursive)
        return True
    except TimeoutError:
        return False

@_check_existence
def getnodes(parent, node_type=None, node_name=None, timeout=_DEFAULT_TIMEOUT,
             visible=True, sensitive=True, recursive=True, **kwargs):
    predicate = AnabotPredicate(
        node_type, node_name, showing=visible, sensitive=sensitive, **kwargs
    )
    log_screenshot()
    exception = TimeoutError("No predicate matches within timeout period", locals())
    return attempted_retries(
        timeout, exception,
        parent.findChildren, predicate, recursive
    )

@_check_existence
def getnode(parent, node_type=None, node_name=None, timeout=_DEFAULT_TIMEOUT,
            visible=True, sensitive=True, recursive=True, **kwargs):
    predicate = AnabotPredicate(
        node_type, node_name, showing=visible, sensitive=sensitive, **kwargs
    )
    log_screenshot()
    exception = TimeoutError("No predicate matches within timeout period", locals())
    return attempted_retries(
        timeout, exception,
        parent.findChild, predicate, recursive, retry=False
    )

def getnode_scroll(parent, node_type=None, node_name=None,
                   timeout=_DEFAULT_TIMEOUT, sensitive=True,
                   recursive=True):
    for x in range(timeout):
        try:
            nodes = getnodes(parent, node_type, node_name, _DEFAULT_TIMEOUT,
                             None, sensitive, recursive)
        except TimeoutError:
            continue
        try:
            node = [n for n in nodes if getparent(n, "scroll pane").showing][0]
            break
        except IndexError:
            pass
        time.sleep(1)
    else:
        raise TimeoutError("No predicate matches within timeout period", locals())
    scrollto(node)
    return node

def getparent(child, node_type=None, node_name=None):
    predicate = GenericPredicate(roleName=node_type, name=node_name)
    return child.findAncestor(predicate)

def getparents(child, node_type=None, node_name=None):
    parents = []
    while True:
        parent = getparent(child, node_type, node_name)
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

    for i in range(items.index(item), len(items)):
        if criteria(items[i]) and items[i] != item:
            distance -= 1
        if distance == 0:
            return items[i]
    return None


@_check_existence
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


@_check_existence
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


def getselected(parent, visible=True):
    return getnodes(parent, visible=visible, selected=True)

def log_screenshot(wait=None, progress_only=False):
    """Make screenshot. Check digest of new screenshot, if it's same as
    previous one, ignore it. Otherwise, log it

    """
    global _SCREENSHOT_NUM
    global _SCREENSHOT_SUM
    global _SCREENSHOT_PROGRESS_SUM
    last_sum = _SCREENSHOT_SUM
    num = _SCREENSHOT_NUM+1
    target_path = '/var/run/anabot/%02d-screenshot.png' % num
    last_progress_sum = _SCREENSHOT_PROGRESS_SUM
    progress_name = '999-last-screenshot.png'

    screenshot(target_path, wait)

    sha1sum = hashlib.sha1()
    with open(target_path, 'rb') as new_file:
        sha1sum.update(new_file.read())
    new_sum = sha1sum.digest()

    _SCREENSHOT_PROGRESS_SUM = new_sum

    if last_progress_sum != new_sum:
        logger.debug('Sending "progress" screenshot')
        flags = {teres.bkr_handlers.REUPLOAD: True}
        reporter.send_file(target_path, progress_name, flags=flags)
    if progress_only:
        return

    if last_sum == new_sum:
        os.unlink(target_path)
        logger.debug('Removing duplicit screenshot')
        return
    logger.debug('Using new screenshot')
    _SCREENSHOT_NUM += 1
    _SCREENSHOT_SUM = new_sum
    reporter.send_file(target_path)

def screenshot(target_path, wait=None):
    if wait is not None:
        time.sleep(wait)
    os.system('%s %s' % (screenshot_executable, target_path))

def get_attr(element, name, default=None):
    try:
        xpath = "./@%s" % name
        return str(element.xpathEval(xpath)[0].getContent())
    except libxml2.xpathError:
        raise Exception("Incorrect xpath expression: '%s'" % xpath)
    except IndexError:
        return default

def get_attr_bool(element, name, default=None):
    value = str(get_attr(element, name, default)).lower()
    allowed_false = ("0", "off", "false")
    allowed_true = ("1", "on", "true")
    allowed = allowed_false + allowed_true

    if not value in allowed:
        raise ValueError("Attribute '%s' contains an invalid value '%s'. Allowed values are: %s" %
            (name, value, ", ".join(allowed)))
    return value in allowed_true

def hold_key(keyName):
    return key_action(keyName, "press")

def release_key(keyName):
    return key_action(keyName, "release")

def press_key(keyName):
    return key_action(keyName, "pressrelease")

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
    # pylint: disable=no-value-for-parameter
    pyatspi.Registry.generateKeyboardEvent(keyCode, None, actions[action])
    dogtail.rawinput.doTypingDelay()

def type_text(text):
    # need to import dogtail.rawinput after display is on, so this is probably
    # the best place for it
    import dogtail.rawinput # pylint: disable=import-error
    dogtail.rawinput.typeText(text)

@_check_existence
def clear_text(node):
    node.keyCombo("<Control>a")
    node.keyCombo("<Delete>")

@_check_existence
def dump(node, filename=None):
    reporter.log_debug("Dumping node")
    dogtail.dump.plain(node, output=filename)
    reporter.log_debug("Node dumped")

MOUSE_SCROLL_UP = 4
MOUSE_SCROLL_DOWN = 5
MOUSE_SCROLL_LEFT = 6
MOUSE_SCROLL_RIGHT = 7
OUTSIDE = -2147483648
SCROLL_STEP = 15
INSIDE_INTOLERANCE = 2 # in pixels

@_check_existence
def _change_value(node, diff):
    node.value += diff

@_check_existence
def scrollto(node):
    def getcenter(node):
        return (
            node.position[0] + node.size[0] / 2,
            node.position[1] + node.size[1] / 2
        )

    def getcorners(node):
        return (
            (node.position[0], node.position[1]),
            (node.position[0] + node.size[0], node.position[1] + node.size[1])
        )

    scroll = getparent(node, "scroll pane")
    logger.debug("Scroll pane: %s" % scroll)
    logger.debug("Scroll location: %s" % repr(scroll.position))
    logger.debug("Scroll size: %s" % repr(scroll.size))
    def scroll_dirs():
        corners = getcorners(scroll)
        # directions are in fact mouse button numbers
        # widget may be completely off screen
        if node.position == (-(2**31), -(2**31)):
            return None, None
        center = getcenter(node)
        dirx, diry = 0, 0
        if center[0] - INSIDE_INTOLERANCE < corners[0][0]:
            dirx = -1
        if center[0] + INSIDE_INTOLERANCE > corners[1][0]:
            if dirx != 0:
                dirx = 0
            else:
                dirx = 1
        if center[1] - INSIDE_INTOLERANCE < corners[0][1]:
            diry = -1
        if center[1] + INSIDE_INTOLERANCE > corners[1][1]:
            if diry != 0:
                diry = 0
            else:
                diry = 1
        return dirx, diry

    if scroll_dirs() == (0, 0):
        return

    xbar = None
    ybar = None
    scroll_up = lambda: None
    scroll_down = lambda: None
    scroll_left = lambda: None
    scroll_right = lambda: None
    scrollbars = getnodes(scroll, "scroll bar", recursive=False, visible=None)
    # GTK rebase caused that scrollbars may be hidden and are visible only
    # when mouse is over them, or when there's some mouse activity in
    # corresponding scroll pane (but in that case, it's showing differently).

    # The scrolling itself is unfortunately done by direct changing of
    # scrollbars value, since it's position is not available anymore and
    # it (or scroll pane) doesn't provide any action for this.
    for scrollbar in scrollbars:
        if scrollbar.size == (1, 1):
            # Ignore this scrollbar, it's present in ATK tree, not visible
            # and not functional. It should be scrollbar for dimension that
            # doesn't need scrollbar now.
            continue
        elif scrollbar.size[0] > scrollbar.size[1]:
            logger.debug("Setting x scrollbar")
            xbar = scrollbar
            scroll_left = functools.partial(_change_value, xbar, -SCROLL_STEP)
            scroll_right = functools.partial(_change_value, xbar, SCROLL_STEP)
        else:
            logger.debug("Setting y scrollbar")
            ybar = scrollbar
            scroll_up = functools.partial(_change_value, ybar, -SCROLL_STEP)
            scroll_down = functools.partial(_change_value, ybar, SCROLL_STEP)

    def toUp():
        logger.debug("Scrolling up")
        if ybar is not None:
            while ybar.value != 0:
                scroll_up()

    def toLeft():
        logger.debug("Scrolling left")
        if xbar is not None:
            while xbar.value != 0:
                scroll_left()

    def scroll_to_screen():
        # widget is outside
        def inside():
            return scroll_dirs() != (None, None)
        if not inside():
            # scroll through all possible points in view
            # this is done similar way as typewriter types
            toUp()
            toLeft()
            while not inside():
                logger.debug("getting there")
                if xbar is not None:
                    logger.debug("we have xbar")
                    while xbar.value < xbar.maxValue:
                        logger.debug("scrolling right")
                        scroll_right()
                        if inside():
                            logger.debug("inside return!")
                            return
                    toLeft()
                logger.debug("scrolling down")
                scroll_down()
            logger.debug("inside!")

    scroll_to_screen()
    while scroll_dirs() != (0,0):
        logger.debug("Node: %s" % node)
        logger.debug("Location: %s" % repr(node.position))
        logger.debug("Scroll direction: %s" % repr(scroll_dirs()))
        if scroll_dirs()[0] == -1:
            logger.debug("Scroll left")
            scroll_left()
        if scroll_dirs()[0] == 1:
            logger.debug("Scroll right")
            scroll_right()
        if scroll_dirs()[1] == -1:
            logger.debug("Scroll up")
            scroll_up()
        if scroll_dirs()[1] == 1:
            logger.debug("Scroll down")
            scroll_down()

    logger.debug("Everything should be fine now")
    logger.debug("Scroll pane: %s" % scroll)
    logger.debug("Scroll location: %s" % repr(scroll.position))
    logger.debug("Scroll size: %s" % repr(scroll.size))
    logger.debug("Node: %s" % node)
    logger.debug("Location: %s" % repr(node.position))
    logger.debug("Size: %s" % repr(node.size))
    logger.debug("Scroll direction: %s" % repr(scroll_dirs()))


def combo_scroll(item, point=True, click=None, doubleclick=None):
    # need to import dogtail.rawinput after display is on, so this is probably
    # the best place for it
    import dogtail.rawinput # pylint: disable=import-error
    # I'm aware of problem with not detectable arrows that cover menu items
    # However, following code should work
    def yborders(i):
        return i.position[1], i.position[1] + i.size[1]
    menu = getparent(item, "menu")

    def do_actions():
        centerx = item.position[0] + item.size[0]/2
        if abs(yborders(item)[0] - yborders(menu)[0]) > abs(yborders(item)[1] - yborders(menu)[1]):
            posy = yborders(item)[0]+1
        else:
            posy = yborders(item)[1]-1
        # ensure that the item is fully visible by pointing at it
        if point:
            dogtail.rawinput.absoluteMotion(centerx, posy)
        if click is not None:
            dogtail.rawinput.click(centerx, posy, click)
        if doubleclick is not None:
            dogtail.rawinput.doubleClick(centerx, posy, doubleclick)

    miny, maxy = yborders(menu)
    # item should be inside of menu borders, so don't scroll
    if yborders(item)[0] > miny and yborders(item)[1] < maxy:
        do_actions()
        return

    previous, following = item, item
    if getnode(menu, "menu item") != item: # item is not first
        previous = getsibling(item, -1, "menu item")
    if getnodes(menu, "menu item")[-1] != item: # item is not last
        following = getsibling(item, 1, "menu item")

    while yborders(previous)[0] < miny:
        menu.click(MOUSE_SCROLL_UP)
    while yborders(following)[1] > maxy:
        menu.click(MOUSE_SCROLL_DOWN)

    do_actions()

@_check_existence
def handle_checkbox(node, element):
    value = get_attr(element, 'checked')
    req_checked = (value == 'yes')
    if node.checked != req_checked:
        node.click()

@_check_existence
def check_checkbox(node, element, name, message="%(name)s is %(found)s, expected: %(expected)s", status_true='checked', status_false='unchecked'):
    if isinstance(element, libxml2.xmlNode):
        req_checked = get_attr(element, 'checked', 'yes') == 'yes'
    else:
        req_checked = bool(element)

    result = (node.checked == req_checked)

    # get msg strings
    found = status_false
    if node.checked:
        found = status_true
    expected = status_false
    if req_checked:
        expected = status_true

    msg = message % {'name': name, 'found': found, 'expected': expected }
    return (result, msg)

def merge_lists(lists):
    merged_list = []
    for member in lists:
        for item in member:
            merged_list.append(item)

    return merged_list
