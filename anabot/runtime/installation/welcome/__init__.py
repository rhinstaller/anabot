import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getselected
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from .common import set_language

import time

# submodules
from . import language, locality, beta_dialog

_local_path = '/installation/welcome'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    welcome = getnode(app_node, "panel", "WELCOME")
    set_language(welcome)
    default_handler(element, app_node, welcome)

@handle_chck('')
def base_check(element, app_node, local_node):
    try:
        welcome = getnode(app_node, "panel", "WELCOME", visible=False)
        return True
    except TimeoutError:
        return False

@handle_act('/continue')
def continue_handler(element, app_node, local_node):
    try:
        getnode(local_node, "push button", "_Continue").click()
    except TimeoutError:
        return False
    return True
