import re

import libxml2
import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from .actionresult import ActionResultFail, ActionResultNone, ActionResultPass

from .functions import get_attr, log_screenshot, dump
from .handlers import ACTIONS, CHECKS
from .results import RESULTS, action_result
from .decorators import handle_action, handle_check
from . import universal

NODE_NUM = re.compile(r'\[[0-9]+\]')

def _check_result(result):
    if result is None:
        return ActionResultNone()
    reason = None
    if type(result) == type(tuple()):
        result, reason = result
        if result:
            return ActionResultPass()
        else:
            return ActionResultFail(reason)
    elif type(result) == type(bool()):
        if result:
            return ActionResultPass()
        else:
            return ActionResultFail()
    return result

def get_handler_check(element):
    raw_node_path = element.nodePath()
    node_path = re.sub(NODE_NUM, '', raw_node_path)
    node_name = element.name

    hnd = ACTIONS.get(node_path) or ACTIONS.get(node_name) or ACTIONS.get(None)
    chck = CHECKS.get(node_path) or CHECKS.get(node_name) or CHECKS.get(None)

    return hnd, chck

def handle_step(element, app_node, local_node):
    raw_node_path = element.nodePath()
    node_path = re.sub(NODE_NUM, '', raw_node_path)
    node_line = element.lineNo()
    policy = get_attr(element, "policy", "should_pass")
    fail_type = get_attr(element, "fail_type")
    handler, check = get_handler_check(element)
    reporter.log_info("Processing: %s" % raw_node_path)
    if policy in ("should_pass", "should_fail", "may_fail"):
        result = handler(element, app_node, local_node)
        RESULTS[raw_node_path] = _check_result(result)
    result = _check_result(check(element, app_node, local_node))
    if policy == "may_fail":
        return
    if result == None:
        reporter.log_error("Check didn't return any result for: %s line: %d" % (node_path, node_line))
    if policy in ("should_pass", "just_check"):
        if result:
            reporter.log_pass("Check passed for: %s line: %d" % (node_path, node_line))
        else:
            reporter.log_fail("Check failed for: %s line: %d" % (node_path, node_line))
    if policy in ("should_fail", "just_check_fail"):
        if result:
            reporter.log_fail("Unexpected pass for: %s line: %d" %
                              (node_path, node_line))
        if result == False:
            if fail_type is None:
                reporter.log_pass("Expected failure for: %s line: %d" %
                                  (node_path, node_line))
            elif fail_type == result.fail_type:
                reporter.log_pass("Expected failure with specified type "
                                  "for: %s line: %d" % (node_path, node_line))
            else:
                reporter.log_fail("Wrong failure type for: %s line: %d, "
                                  "expected type was: %s"
                                  % (node_path, node_line, fail_type))
    if result.reason is not None:
        reporter.log_info("Reason was: %s" % result.reason)
    try:
        if result.fail_type is not None:
            reporter.log_info("Failure type was: %s" % result.fail_type)
    except AttributeError:
        pass
    log_screenshot()

def default_handler(element, app_node, local_node, waitfunc=None):
    for child in element.xpathEval("./*"):
        if waitfunc is not None:
            waitfunc()
        handle_step(child, app_node, local_node)
    return True

@handle_action(None)
def unimplemented_handler(element, app_node, local_node):
    reporter.log_error('Unhandled element: %s' % element.nodePath())
    return default_handler(element, app_node, local_node)

@handle_check(None)
def unimplemented_handler_check(element, app_node, local_node):
    node_path = element.nodePath()
    try:
        result = action_result(node_path)
        if result is not None:
            reporter.log_debug('Using result reported by handler for element: %s' % node_path)
            return result
    except KeyError:
        pass
    reporter.log_error('Unhandled check for element: %s' % node_path)
