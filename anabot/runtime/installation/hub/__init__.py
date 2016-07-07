import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase
from time import sleep

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, TimeoutError
from anabot.runtime.translate import tr

# submodules
from . import datetime, keyboard, partitioning, software_selection, oscap_addon

@handle_action('/installation/hub')
def hub_handler(element, app_node, local_node):
    local_node = getnode(app_node, "panel", tr("INSTALLATION SUMMARY"))
    default_handler(element, app_node, local_node)

@handle_check('/installation/hub')
@check_action_result
def hub_check(element, app_node, local_node):
    # TODO: check that the hub is not visible anymore
    return True

@handle_action('/installation/hub/begin_installation')
def begin_installation_handler(element, app_node, local_node):
    try:
        begin_button = getnode(app_node, "push button",
                               tr("_Begin Installation", context="GUI|Summary"))
    except TimeoutError:
        return (False, 'Couln\'t find clickable "Begin installation" button.')
    begin_button.click()
    return True

@handle_check('/installation/hub/begin_installation')
def begin_installation_check(element, app_node, local_node):
    if action_result(element) != None:
        logger.debug('begin_installation returns action_result')
        return action_result(element)
    try:
        begin_button = getnode(
            app_node,
            "push button",
            tr("_Begin Installation", context="GUI|Summary"),
            sensitive=None
        )
    except TimeoutError:
        return (False, 'Couln\'t find "Begin installation" button.')
    for i in xrange(5):
        if begin_button.sensitive:
            return True
        sleep(1)
    return (False, '"Begin installation" button is not clickable')
