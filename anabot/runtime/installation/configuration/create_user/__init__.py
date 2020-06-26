# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

from anabot.conditions import is_distro_version, has_feature_hub_config
from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, TimeoutError, getparent, getsibling, handle_checkbox, check_checkbox, clear_text
from anabot.runtime.translate import tr
from anabot.runtime.functions import getnode_scroll, scrollto
from anabot.runtime.hooks import run_posthooks
from anabot.runtime.installation.common import done_handler

# import advanced dialog
from . import advanced

_local_path = '/installation/configuration/create_user'
_local_path_hub = '/installation/hub/create_user'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
handle_act_hub = lambda x: handle_action(_local_path_hub + x)
handle_chck_hub = lambda x: handle_check(_local_path_hub + x)

SPOKE_SELECTOR="_User Creation"
if is_distro_version('rhel', 7):
    SPOKE_SELECTOR="_USER CREATION"

strings = {
    'full_name': 'Full Name',
    'user_name': 'User Name',
    'make_admin': 'Make this user administrator',
    'require_password': 'Require a password to use this account',
    'password': '_Password',
    'confirm_password': 'Confirm Password'
}
if has_feature_hub_config():
    strings.update({
        'make_admin': '_Make this user administrator',
        'require_password': '_Require a password to use this account',
    })

@handle_act_hub('')
@handle_act('')
def user_spoke_handler(element, app_node, local_node):
    try:
        user_spoke = getnode_scroll(app_node, "spoke selector",
                                     tr(SPOKE_SELECTOR, context="GUI|Spoke"))
    except:
        return (False, "User spoke selector not found or not clickable")
    user_spoke.click()
    try:
        user_panel = getnode(app_node, "panel", tr("CREATE USER"))
    except TimeoutError:
        return (False, "User creation spoke not found")
    default_handler(element, app_node, user_panel)

@handle_chck_hub('')
@handle_chck('')
@check_action_result
def user_spoke_check(element, app_node, local_node):
    try:
        user_panel = getnode(app_node, "panel", tr("CREATE USER"))
        return (False, "User spoke is still visible")
    except TimeoutError:
        return True

@handle_act_hub('/full_name')
@handle_act('/full_name')
def user_full_name_handler(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr(strings['full_name']))
    value = get_attr(element, 'value')
    entry.typeText(value)

@handle_chck_hub('/full_name')
@handle_chck('/full_name')
def user_full_name_check(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr(strings['full_name']))
    value = get_attr(element, 'value')
    if (value is None):
        value = ''
    if entry.text == value:
        return True
    return (False, "users full name ('%s') differs from expected one ('%s')" % (entry.text, value))

@handle_act_hub('/username')
@handle_act('/username')
def user_username_handler(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr(strings['user_name']))
    value = get_attr(element, 'value')
    if not (value is None):
        entry.typeText(value)

@handle_chck_hub('/username')
@handle_chck('/username')
def user_username_check(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr(strings['user_name']))
    value = get_attr(element, 'value')
    if (value is None):
        value = ''
    if entry.text == value:
        return True
    return (False, "username ('%s') differs from expected one ('%s')" % (entry.text, value))

@handle_act_hub('/is_admin')
@handle_act('/is_admin')
def user_is_admin_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr(strings['make_admin'], context="GUI|User")) # translation bug: "Udělat tohot uživatele správcem"
    handle_checkbox(checkbox, element)

@handle_chck_hub('/is_admin')
@handle_chck('/is_admin')
def user_is_admin_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr(strings['make_admin'], context="GUI|User"))
    return check_checkbox(checkbox, element, 'Make user administrator')

@handle_act_hub('/require_password')
@handle_act('/require_password')
def user_require_passwd_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr(strings['require_password'], context="GUI|User"))
    handle_checkbox(checkbox, element)

@handle_chck('/require_password')
def user_require_passwd_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr(strings['require_password'], context="GUI|User"))
    return check_checkbox(checkbox, element, 'Account requires password')

@handle_act_hub('/password')
@handle_act('/password')
def user_password_handler(element, app_node, local_node):
    entry = getnode(local_node, "password text", tr(strings['password'], context="GUI|User"))
    password = get_attr(element, 'value')
    clear_text(entry)
    entry.typeText(password)
    return True #cannot verify password via ATK

@handle_act_hub('/confirm_password')
@handle_act('/confirm_password')
def user_confirm_password_handler(element, app_node, local_node):
    logger.debug("searching for %s" % tr('Confirm password'))
    entry = getnode(local_node, "password text", tr(strings['confirm_password'])) # translation error  label "_Povrďte heslo"
    password = get_attr(element, 'value')
    clear_text(entry)
    entry.typeText(password)
    return True #cannot verify password via ATK

@handle_act_hub('/done')
@handle_act('/done')
def user_done_handler(element, app_node, local_node):
    try:
        done_handler(element, app_node, local_node)
    except TimeoutError:
        return (False, "Done button not found or not clickable")
    try:
        user_panel = getnode(app_node, "panel", tr("CREATE USER"))
        return (False, "User spoke is still present")
    except TimeoutError:
        return True
    return False
