import re

import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from .functions import get_attr, screenshot
from .decorators import ACTIONS, CHECKS, handle_action, handle_check

NODE_NUM = re.compile(r'\[[0-9]+\]')

RESULTS = {}

def _check_result_reason(result):
    if result is None:
        return None, None
    reason = None
    if type(result) != type(bool()):
        result, reason = result
    return (result, reason)

def handle_step(element, app_node, local_node):
    raw_node_path = element.nodePath()
    node_path = re.sub(NODE_NUM, '', raw_node_path)
    node_line = element.lineNo()
    policy = get_attr(element, "policy", "should_pass")
    handler_path = node_path
    reporter.log_debug("Processing: %s" % raw_node_path)
    if handler_path not in ACTIONS:
        handler_path = None
    if policy in ("should_pass", "should_fail", "may_fail"):
        RESULTS[raw_node_path] = ACTIONS.get(handler_path)(element,
                                                           app_node,
                                                           local_node)
    if handler_path is None:
        return
    if handler_path not in CHECKS:
        handler_path = None
    result, reason = _check_result_reason(CHECKS.get(handler_path)(element, app_node, local_node))
    if policy == "may_fail":
        return
    if policy in ("should_pass", "just_check"):
        if result:
            reporter.log_pass("Check passed for: %s line: %d" % (node_path, node_line))
        else:
            reporter.log_fail("Check failed for: %s line: %d" % (node_path, node_line))
    if policy in ("should_fail", "just_check_fail"):
        if not result:
            reporter.log_pass("Expected failure for: %s line: %d" %
                              (node_path, node_line))
        else:
            reporter.log_fail("Unexpected pass for: %s line: %d" %
                              (node_path, node_line))
    if reason is not None:
        reporter.log_info("Reason was: %s" % reason)
    screenshot()

def default_handler(element, app_node, local_node):
    if element.name == 'debug_stop':
        from time import sleep
        import os
        RESUME_FILEPATH = '/var/run/anabot/resume'
        logger.debug('Running /opt/dump.py due to DEBUG STOP')
        os.system('/opt/dump.py')
        logger.debug('DEBUG STOP at %s, touch %s to resume',
                     element.nodePath(), RESUME_FILEPATH)
        while not os.path.exists(RESUME_FILEPATH):
            sleep(0.1)
        os.remove(RESUME_FILEPATH)
    for child in element.xpathEval("./*"):
        handle_step(child, app_node, local_node)

@handle_action(None)
def unimplemented_handler(element, app_node, local_node):
    reporter.log_error('Unhandled element: %s' % element.nodePath())
    default_handler(element, app_node, local_node)

@handle_check(None)
def unimplemented_handler_check(element, app_node, local_node):
    node_path = element.nodePath()
    try:
        result = RESULTS[node_path]
        if result is not None:
            reporter.log_debug('Using result reported by handler for element: %s' % node_path)
            return result
    except KeyError:
        pass
    reporter.log_error('Unhandled check for element: %s' % node_path)
