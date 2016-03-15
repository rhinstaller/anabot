# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, TimeoutError, getparent, getsibling
from anabot.runtime.translate import tr

_local_path = '/installation/configuration'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_act('/reboot')
def reboot_handler(element, app_node, local_node):
    logger.debug("WAITING FOR REBOOT")
    reboot_button = getnode(app_node, "push button",
                            tr("_Reboot", context="GUI|Progress"),
                            timeout=float("inf"))
    # Anabot POST hooks will be run here
    reboot_button.click()

@handle_act('/root_password')
def root_password_handler(element, app_node, local_node):
    root_password_spoke = getnode(app_node, "spoke selector",
                                  tr("_ROOT PASSWORD", context="GUI|Spoke"))
    root_password_spoke.click()
    try:
        root_password_panel = getnode(app_node, "panel", tr("ROOT PASSWORD"))
    except TimeoutError:
        return (False, "Root password spoke not found")
    default_handler(element, app_node, root_password_panel)

@handle_act('/root_password/password')
def root_password_text_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text", tr("Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_act('/root_password/confirm_password')
def root_password_confirm_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text",
                             tr("Confirm Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_act('/root_password/done')
def root_password_done_handler(element, app_node, local_node):
    try:
        root_password_done = getnode(local_node, "push button",
                                     tr("_Done", False))
    except TimeoutError:
        return (False, "Done button not found or not clickable")

    root_password_done.click()
    return True # done for password found and was clicked

@handle_act('/create_user')
def user_spoke_handler(element, app_node, local_node):
    user_spoke = getnode(app_node, "spoke selector",
                                  tr("_USER CREATION", context="GUI|Spoke"))
    user_spoke.click()
    try:
        user_panel = getnode(app_node, "panel", tr("CREATE USER"))
    except TimeoutError:
        return (False, "User creation spoke not found")
    default_handler(element, app_node, user_panel)

@handle_act('/create_user/full_name')
def user_full_name_handler(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr('Full Name'))
    value = get_attr(element, 'value')
    entry.typeText(value)

@handle_chck('/create_user/full_name')
def user_full_name_check(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr('Full Name'))
    value = get_attr(element, 'value')
    if (value is None):
        value = ''
    if entry.text == value:
        return True
    return (False, "users full name ('%s') differs from expected one ('%s')" % (entry.text, value))

@handle_act('/create_user/username')
def user_username_handler(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr('User name'))
    value = get_attr(element, 'value')
    if not (value is None):
        entry.typeText(value)

@handle_chck('/create_user/username')
def user_username_check(element, app_node, local_node):
    entry = getnode(local_node, 'text', tr('User name'))
    value = get_attr(element, 'value')
    if (value is None):
        value = ''
    if entry.text == value:
        return True
    return (False, "username ('%s') differs from expected one ('%s')" % (entry.text, value))

@handle_act('/create_user/is_admin')
def user_is_admin_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Make this user administrator', context="GUI|User")) # translation bug: "Udělat tohot uživatele správcem"
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked != value:
        checkbox.click()

@handle_chck('/create_user/is_admin')
def user_is_admin_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Make this user administrator', context="GUI|User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked == value:
        return True
    return False
        

@handle_act('/create_user/require_password')
def user_require_passwd_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Require a password to use this account', context="GUI|User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked != value:
        checkbox.click()

@handle_chck('/create_user/require_password')
def user_require_passwd_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Require a password to use this account', context="GUI|User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked == value:
        return True
    return False

@handle_act('/create_user/password')
def user_password_handler(element, app_node, local_node):
    entry = getnode(local_node, "password text", tr('_Password', context="GUI|User"))
    password = get_attr(element, 'value')
    entry.typeText(password)
    return True #cannot verify password via ATK

@handle_act('/create_user/confirm_password')
def user_confirm_password_handler(element, app_node, local_node):
    print "searching for %s" % tr('Confirm password')
    entry = getnode(local_node, "password text", tr('Confirm Password')) # translation error  label "_Povrďte heslo"
    password = get_attr(element, 'value')
    entry.typeText(password)
    return True #cannot verify password via ATK

@handle_act('/create_user/advanced')
def user_advanced_handler(element, app_node, local_node):
    button = getnode(local_node, "push button", tr('_Advanced...', context="GUI|User"))
    button.click()
    dialog_label = getnode(app_node, "label", tr('ADVANCED USER CONFIGURATION'))
    advanced_dialog = getparent(dialog_label, node_type="dialog")
    default_handler(element, app_node, advanced_dialog)

@handle_chck('/create_user/advanced')
def user_advanced_check(element, app_node, local_node):
    button = getnode(local_node, "push button", tr('_Advanced...', context="GUI|User"), sensitive = None)
    return button.sensitive

@handle_act('/create_user/advanced/home')
def user_adv_homedir_handler(element, app_node, local_node):
    label = getnode(local_node, "label", tr('Home _directory:', context="GUI|Advanced User"))
    entry = getsibling(label, 1, node_type="text")
    homedir = get_attr(element, 'value')
    entry.typeText(homedir)

@handle_chck('/create_user/advanced/home')
def user_adv_homedir_check(element, app_node, local_node):
    label = getnode(local_node, "label", tr('Home _directory:', context="GUI|Advanced User"))
    print 'found homedir label'
    entry = getsibling(label, 1, node_type="text")
    homedir = get_attr(element, 'value')
    if entry.text == homedir:
        return True
    return (False, "Homedir '%s' is different than expected '%s'" % (entry.text, homedir))

@handle_act('/create_user/advanced/manual_uid')
def user_adv_manual_uid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _user ID manually:', context="GUI|Advanced User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked != value:
        checkbox.click()

@handle_chck('/create_user/advanced/manual_uid')
def user_adv_manual_uid_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _user ID manually:', context="GUI|Advanced User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked == value:
        return True
    return False

@handle_act('/create_user/advanced/uid')
def user_adv_uid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _user ID manually:', context="GUI|Advanced User"))
    spin_button = getsibling(checkbox, -1, node_type="spin button", sensitive=None)
    value = get_attr(element, 'value')
    spin_button.typeText(value)

@handle_act('/create_user/advanced/manual_gid')
def user_adv_manual_gid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _group ID manually:', context="GUI|Advanced User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked != value:
        checkbox.click()

@handle_chck('/create_user/advanced/manual_gid')
def user_adv_manual_gid_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _group ID manually:', context="GUI|Advanced User"))
    value = get_attr(element, 'checked')
    if value == 'yes':
        value = True
    else:
        value = False
    if checkbox.checked == value:
        return True
    return False

@handle_act('/create_user/advanced/gid')
def user_adv_gid_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr('Specify a _group ID manually:', context="GUI|Advanced User"))
    spin_button = getsibling(checkbox, -2, node_type="spin button", sensitive=None)
    value = get_attr(element, 'value')
    spin_button.typeText(value)

@handle_act('/create_user/advanced/groups')
def user_adv_groups_handler(element, app_node, local_node):
    label = getnode(local_node, "label", tr('_Add user to the following groups:', context="GUI|Advanced User"))
    entry = getsibling(label, 1, node_type="text")
    groups = get_attr(element, 'value')
    entry.typeText(groups)

@handle_act('/create_user/advanced/cancel')
def user_adv_cancel_handler(element, app_node, local_node):
    button = getnode(local_node, "push button", tr("_Cancel", context="GUI|Advanced User"))
    button.click()

@handle_chck('/create_user/advanced/cancel')
def user_adv_cancel_check(element, app_node, local_node):
    try:
        dialog_label = getnode(app_node, "label", tr('ADVANCED USER CONFIGURATION'))
        return (False,"Advanced user dialog is still present")
    except TimeoutError:
        return True
    return False

@handle_act('/create_user/advanced/save')
def user_adv_save_handler(element, app_node, local_node):
    button = getnode(local_node, "push button", tr("_Save Changes", context="GUI|Advanced User"))
    button.click()

@handle_chck('/create_user/advanced/save')
def user_adv_save_check(element, app_node, local_node):
    try:
        dialog_label = getnode(app_node, "label", tr('ADVANCED USER CONFIGURATION'))
        return (False,"Advanced user dialog is still present")
    except TimeoutError:
        return True
    return False

@handle_act('/create_user/done')
def user_done_handler(element, app_node, local_node):
    try:
        done_btn = getnode(local_node, "push button",
                                     tr("_Done", False))
    except TimeoutError:
        return (False, "Done button not found or not clickable")
    done_btn.click()
    try:
        user_panel = getnode(app_node, "panel", tr("CREATE USER"))
        return (False, "User spoke is still present")
    except TimeoutError:
        return True
    return False 

