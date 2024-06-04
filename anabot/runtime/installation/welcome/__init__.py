import logging
logger = logging.getLogger('anabot')
import time

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getnodes, getselected, disappeared
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from .common import set_language

# submodules
from . import language, locality, beta_dialog, storage_error_dialog

_local_path = '/installation/welcome'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
#    welcome = getnode(app_node, "panel", "WELCOME")
    # language is not set yet, so we can't look up the panel based on a (translated) string
    welcome = getnodes(app_node, "panel")[7]
    set_language(welcome)
    default_handler(element, app_node, welcome)

@handle_chck('')
def base_check(element, app_node, local_node):
    return disappeared(app_node, "panel", tr("WELCOME"))

@handle_act('/continue')
def continue_handler(element, app_node, local_node):
    try:
        continue_button = getnode(app_node, "push button", tr("_Continue", False, "GUI|Standalone Navigation"))
    except TimeoutError:
        return False
    continue_button.click()
    return True
