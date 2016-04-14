# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, TimeoutError, getparent, getsibling
from anabot.runtime.translate import tr
from anabot.runtime.hooks import run_posthooks

_local_path = '/installation/configuration/root_password'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def root_password_handler(element, app_node, local_node):
    root_password_spoke = getnode(app_node, "spoke selector",
                                  tr("_ROOT PASSWORD", context="GUI|Spoke"))
    root_password_spoke.click()
    try:
        root_password_panel = getnode(app_node, "panel", tr("ROOT PASSWORD"))
    except TimeoutError:
        return (False, "Root password spoke not found")
    default_handler(element, app_node, root_password_panel)

@handle_act('/password')
def root_password_text_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text", tr("Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_act('/confirm_password')
def root_password_confirm_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text",
                             tr("Confirm Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_act('/done')
def root_password_done_handler(element, app_node, local_node):
    try:
        root_password_done = getnode(local_node, "push button",
                                     tr("_Done", False))
    except TimeoutError:
        return (False, "Done button not found or not clickable")

    root_password_done.click()
    return True # done for password found and was clicked

