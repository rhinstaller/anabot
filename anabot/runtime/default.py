import re

import logging
logger = logging.getLogger('anabot')

from functions import get_attr, screenshot
from decorators import ACTIONS, CHECKS, handle_action, handle_check

NODE_NUM = re.compile(r'\[[0-9]+\]')

def handle_step(element, app_node, local_node):
    node_path = re.sub(NODE_NUM, '', element.nodePath())
    node_line = element.lineNo()
    policy = get_attr(element, "policy", "should_pass")
    handler_path = node_path
    if handler_path not in ACTIONS:
        handler_path = None
    if policy in ("should_pass", "should_fail", "may_fail"):
        ACTIONS.get(handler_path)(element, app_node, local_node)
    if handler_path is None:
        return
    if handler_path not in CHECKS:
        handler_path = None
    if policy in ("should_pass", "just_check"):
        if CHECKS.get(handler_path)(element, app_node, local_node):
            logger.info("Check passed for: %s line: %d", node_path, node_line)
        else:
            logger.error("Check failed for: %s line: %d", node_path, node_line)
    if policy in ("should_fail"):
        if not CHECKS.get(handler_path)(element, app_node, local_node):
            logger.info("Expected failure for: %s line: %d", node_path, node_line)
        else:
            logger.error("Unexpected failure for: %s line: %d", node_path, node_line)
    screenshot()

def default_handler(element, app_node, local_node):
    for child in element.xpathEval("./*"):
        handle_step(child, app_node, local_node)

@handle_action(None)
def unimplemented_handler(element, app_node, local_node):
    logger.debug('Unhandled element: %s' % element.nodePath())
    default_handler(element, app_node, local_node)

@handle_check(None)
def unimplemented_handler_check(element, app_node, local_node):
    logger.debug('Unhandled check for element: %s' % element.nodePath())
