# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, TimeoutError, getparent, getsibling, handle_checkbox, check_checkbox
from anabot.runtime.translate import tr
from anabot.runtime.hooks import run_posthooks

_local_path = '/installation/configuration/create_user/advanced'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def user_advanced_handler(element, app_node, local_node):
    button = getnode(local_node, "push button", tr('_Advanced...', context="GUI|User"))
    button.click()
    dialog_label = getnode(app_node, "label", tr('ADVANCED USER CONFIGURATION'))
    advanced_dialog = getparent(dialog_label, node_type="dialog")
    default_handler(element, app_node, advanced_dialog)

@handle_chck('')
def user_advanced_check(element, app_node, local_node):
    button = getnode(local_node, "push button", tr('_Advanced...', context="GUI|User"), sensitive = None)
    return button.sensitive

@handle_act('/home')
def user_adv_homedir_handler(element, app_node, local_node):
    label = getnode(local_node, "label", tr('Home _directory:', context="GUI|Advanced User"))
    entry = getsibling(label, 1, node_type="text")
    homedir = get_attr(element, 'value')
    entry.typeText(homedir)

@handle_chck('/home')
def user_adv_homedir_check(element, app_node, local_node):
    label = getnode(local_node, "label", tr('Home _directory:', context="GUI|Advanced User"))
    print 'found homedir label'
    entry = getsibling(label, 1, node_type="text")
    homedir = get_attr(element, 'value')
    if entry.text == homedir:
        return True
    return (False, "Homedir '%s' is different than expected '%s'" % (entry.text, homedir))

@handle_act('/manual_uid')
def user_adv_manual_uid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _user ID manually:', context="GUI|Advanced User"))
    handle_checkbox(checkbox, element)

@handle_chck('/manual_uid')
def user_adv_manual_uid_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _user ID manually:', context="GUI|Advanced User"))
    return check_checkbox(checkbox, element, 'Manual UID')

@handle_act('/uid')
def user_adv_uid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _user ID manually:', context="GUI|Advanced User"))
    spin_button = getsibling(checkbox, -1, node_type="spin button", sensitive=None)
    value = get_attr(element, 'value')
    spin_button.typeText(value)

@handle_act('/manual_gid')
def user_adv_manual_gid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _group ID manually:', context="GUI|Advanced User"))
    handle_checkbox(checkbox, element)

@handle_chck('/manual_gid')
def user_adv_manual_gid_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _group ID manually:', context="GUI|Advanced User"))
    return check_checkbox(checkbox, element, 'Manual GID')

@handle_act('/gid')
def user_adv_gid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _group ID manually:', context="GUI|Advanced User"))
    spin_button = getsibling(checkbox, -2, node_type="spin button", sensitive=None)
    value = get_attr(element, 'value')
    spin_button.typeText(value)

@handle_act('/groups')
def user_adv_groups_handler(element, app_node, local_node):
    label = getnode(local_node, "label", tr('_Add user to the following groups:', context="GUI|Advanced User"))
    entry = getsibling(label, 1, node_type="text")
    groups = get_attr(element, 'value')
    entry.typeText(groups)

@handle_act('/cancel')
def user_adv_cancel_handler(element, app_node, local_node):
    button = getnode(local_node, "push button", tr("_Cancel", context="GUI|Advanced User"))
    button.click()

@handle_chck('/cancel')
def user_adv_cancel_check(element, app_node, local_node):
    try:
        dialog_label = getnode(app_node, "label", tr('ADVANCED USER CONFIGURATION'))
        return (False,"Advanced user dialog is still present")
    except TimeoutError:
        return True
    return False

@handle_act('/save')
def user_adv_save_handler(element, app_node, local_node):
    button = getnode(local_node, "push button", tr("_Save Changes", context="GUI|Advanced User"))
    button.click()

@handle_chck('/save')
def user_adv_save_check(element, app_node, local_node):
    try:
        dialog_label = getnode(app_node, "label", tr('ADVANCED USER CONFIGURATION'))
        return (False,"Advanced user dialog is still present")
    except TimeoutError:
        return True
    return False

