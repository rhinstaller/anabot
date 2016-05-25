import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, TimeoutError
from anabot.runtime.translate import tr

# submodules
from . import partitioning, software_selection

@handle_action('/installation/hub')
def hub_handler(element, app_node, local_node):
    local_node = getnode(app_node, "panel", tr("INSTALLATION SUMMARY"))
    default_handler(element, app_node, local_node)
    try:
        begin_button = getnode(app_node, "push button",
                               tr("_Begin Installation", context="GUI|Summary"))
    except TimeoutError:
        return (False, 'Couln\'t find "Begin installation" button.')
    begin_button.click()
    return True

@handle_check('/installation/hub')
def hub_check(element, app_node, local_node):
    return action_result(element)
