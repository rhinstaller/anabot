# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

from anabot.conditions import is_distro_version
from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getparent, getsibling, clear_text, handle_checkbox, \
    check_checkbox
from anabot.runtime.errors import TimeoutError, NonexistentError
from anabot.runtime.translate import tr, gtk_tr
from anabot.runtime.hooks import run_posthooks
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.asserts import assertPasswordTextInputEquals as aptie
from anabot.runtime.installation.common import done_handler

_local_path = '/installation/configuration/root_password'
_local_path_hub = '/installation/hub/root_password'

def handle_act(path, *args, **kwargs):
    return handle_action(_local_path + path, *args, **kwargs)

def handle_chck(path, *args, **kwargs):
    return handle_check(_local_path + path, *args, **kwargs)

def handle_act_hub(path, *args, **kwargs):
    return handle_action(_local_path_hub + path, *args, **kwargs)

def handle_chck_hub(path, *args, **kwargs):
    return handle_check(_local_path_hub + path, *args, **kwargs)

def check_rootpw_error(parent_node):
    try:
        warning_bar = getnode(parent_node, "info bar", gtk_tr("Warning"))
        warn_icon = getnode(warning_bar, "icon", gtk_tr("Warning"))
        warn_text = getsibling(warn_icon, 1, "label")
        return (False, warn_text.text)
    except NonexistentError:
        return True

SPOKE_SELECTOR="_Root Password"
if is_distro_version('rhel', 7):
    SPOKE_SELECTOR="_ROOT PASSWORD"

@handle_act_hub('')
@handle_act('')
def root_password_handler(element, app_node, local_node):
    try:
        root_password_spoke = getnode(app_node, "spoke selector",
                                      tr(SPOKE_SELECTOR, context="GUI|Spoke"))
    except:
        return (False, "Root password spoke selector not found or not clickable.")
    root_password_spoke.click()
    try:
        root_password_panel = getnode(app_node, "panel", tr("ROOT PASSWORD"))
    except TimeoutError:
        return (False, "Root password spoke not found")
    default_handler(element, app_node, root_password_panel)
    return True

@handle_chck_hub('')
@handle_chck('')
def root_password_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    try:
        getnode(app_node, "panel", tr("ROOT PASSWORD"))
        return (False, "Root password panel is still visible")
    except TimeoutError:
        return True

PASSWORD_TEXT_NOT_FOUND = NotFound("password text", "password_text_not_found")

def root_password_text_manipulate(element, app_node, local_node, dry_run):
    value = get_attr(element, "value")
    try:
        password_entry = getnode(local_node, "password text", tr("Password"))
    except TimeoutError:
        return PASSWORD_TEXT_NOT_FOUND
    if not dry_run:
        password_entry.click()
        clear_text(password_entry)
        password_entry.typeText(value)
    else:
        return aptie(password_entry, value, 'Root')

@handle_act_hub('/password')
@handle_act('/password')
def root_password_text_handler(element, app_node, local_node):
    root_password_text_manipulate(element, app_node, local_node, False)

@handle_chck_hub('/password')
@handle_chck('/password')
def root_password_text_check(element, app_node, local_node):
    return root_password_text_manipulate(element, app_node, local_node, True)

PASSWORD_CONFIRM_TEXT_NOT_FOUND = NotFound("password confirmation text",
                                           "password_confirm_text_not_found")

def root_password_confirm_manipulate(element, app_node, local_node, dry_run):
    value = get_attr(element, "value")
    try:
        password_entry = getnode(local_node, "password text",
                                tr("Confirm Password"))
    except TimeoutError:
        return PASSWORD_CONFIRM_TEXT_NOT_FOUND
    if not dry_run:
        password_entry.click()
        clear_text(password_entry)
        password_entry.typeText(value)
    else:
        return aptie(password_entry, value, 'Confirm root')

@handle_act_hub('/confirm_password')
@handle_act('/confirm_password')
def root_password_confirm_handler(element, app_node, local_node):
    root_password_confirm_manipulate(element, app_node, local_node, False)

@handle_chck_hub('/confirm_password')
@handle_chck('/confirm_password')
def root_password_confirm_check(element, app_node, local_node):
    return root_password_confirm_manipulate(element, app_node, local_node, True)

handle_act('/done')(done_handler)
handle_act_hub('/done')(done_handler)

@handle_chck_hub('/done')
@handle_chck('/done')
@check_action_result
def root_password_done_check(element, app_node, local_node):
    return check_rootpw_error(local_node)


@handle_act_hub('/lock_root_account')
def lock_root_account_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr("Lock root account", context="GUI|Root Password|Lock root account"))
    handle_checkbox(checkbox, element)

@handle_chck_hub('/lock_root_account')
@check_action_result
def lock_root_account_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr("Lock root account", context="GUI|Root Password|Lock root account"))
    return check_checkbox(checkbox, element, "Lock root account")
