import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes,\
    getparent, clear_text, getsibling
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultPass as Pass, ActionResultFail as Fail
from anabot.variables import set_variable, get_variable

_local_path = '/installation/hub/partitioning'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

BLACK_CIRCLE = u'\u25cf'
LUKS_LABEL_NOT_FOUND = NotFound("Disk encryption passphrase label")
LUKS_DIALOG_NOT_FOUND = NotFound("LUKS panel")
@handle_act('/luks')
def luks_handler(element, app_node, local_node):
    try:
        luks_label = getnode(app_node, "label", tr("DISK ENCRYPTION PASSPHRASE"))
    except TimeoutError:
        return LUKS_LABEL_NOT_FOUND
    try:
        luks_dialog = getparent(luks_label, "dialog")
    except TimeoutError:
        return LUKS_DIALOG_NOT_FOUND
    return default_handler(element, app_node, luks_dialog)

@handle_chck('/luks')
def luks_check(element, app_node, local_node):
    return action_result(element)

def luks_password_manipulate(element, app_node, local_node, dry_run):
    value = get_attr(element, "value")
    # the password entry indeed has index 1 and confirmation entry has index 0
    pw_entry = getnodes(local_node, "password text")[1]
    if not dry_run:
        pw_entry.click()
        clear_text(pw_entry)
        logger.info("Entering LUKS password '%s'" % value)
        pw_entry.typeText(value)
        set_variable("luks_password", value)
    else:
        if len(value)*BLACK_CIRCLE == unicode(pw_entry.text):
            return Pass()
        else:
            return Fail("LUKS password doesn't have expected length.")

@handle_act('/luks/password')
def luks_password_handler(element, app_node, local_node):
    luks_password_manipulate(element, app_node, local_node, False)

@handle_chck('/luks/password')
def luks_password_check(element, app_node, local_node):
    return luks_password_manipulate(element, app_node, local_node, True)

def luks_confirm_password_manipulate(element, app_node, local_node, dry_run):
    value = get_attr(element, "value")
    # the password entry indeed has index 1 and confirmation entry has index 0
    pw_confirm_entry = getnodes(local_node, "password text")[0]
    if not dry_run:
        pw_confirm_entry.click()
        clear_text(pw_confirm_entry)
        logger.info("Entering LUKS confirmation password '%s'" % value)
        pw_confirm_entry.typeText(value)
        set_variable("luks_confirm_password", value)
    else:
        if len(value)*BLACK_CIRCLE == unicode(pw_confirm_entry.text):
            return Pass()
        else:
            return Fail("LUKS confirmation password doesn't have expected length.")

@handle_act('/luks/confirm_password')
def luks_confirm_password_handler(element, app_node, local_node):
    luks_confirm_password_manipulate(element, app_node, local_node, False)

@handle_chck('/luks/confirm_password')
@check_action_result
def luks_confirm_password_check(element, app_node, local_node):
    return luks_confirm_password_manipulate(element, app_node, local_node, True)

@handle_act('/luks/cancel')
def luks_cancel_handler(element, app_node, local_node):
    try:
        cancel_button = getnode(local_node, "push button",
                                tr("_Cancel", context="GUI|Passphrase Dialog"))
        if cancel_button.sensitive:
            cancel_button.click()
        else:
            return NotFound("active \"Cancel\" button")
    except TimeoutError:
        return NotFound("\"Cancel\" button")
    finally:
        set_variable("luks_password", "")
        set_variable("luks_confirm_password", "")

@handle_chck('/luks/cancel')
@check_action_result
def luks_cancel_check(element, app_node, local_node):
    try:
        getnode(app_node, "push button", tr("_Cancel", context="GUI|Passphrase Dialog"))
        return NotFound("active \"Cancel\" button")
    except TimeoutError:
        return Pass()

@handle_act('/luks/save')
def luks_save_handler(element, app_node, local_node):
    try:
        save_button = getnode(local_node, "push button",
                                tr("_Save Passphrase", context="GUI|Passphrase Dialog"))
        if save_button.sensitive:
            save_button.click()
        else:
            return NotFound("active \"Save Passphrase\"")
    except TimeoutError:
        return NotFound("\"save Passphrase\" button")

@handle_chck('/luks/save')
@check_action_result
def luks_save_check(element, app_node, local_node):
    try:
        getnode(app_node, "push button", tr("_save", context="GUI|Passphrase Dialog"))
        return Fail("Active Save Passphrase button found", "button_found")
    except TimeoutError:
        luks_password = get_variable("luks_password")
        luks_confirm_password = get_variable("luks_confirm_password")
        if luks_password == luks_confirm_password:
            return Pass()
        else:
            return Fail("LUKS password and confirmation password don't match: "
                        " '%s' '%s'" % (luks_password, luks_confirm_password))

KB_PANEL_NOT_FOUND = NotFound("Keyboard Layout panel")
KB_ICON_LABEL_NOT_FOUND = NotFound("keyboard layout icon or label")
def luks_keyboard_manipulate(element, app_node, local_node, dry_run):
    required_layout = get_attr(element, "layout")
    try:
        panel = getnode(local_node, "panel", "Keyboard Layout")
    except TimeoutError:
        return KB_PANEL_NOT_FOUND
    try:
        icon = getnode(panel, "icon")
        kb_label = getsibling(icon, 1, "label")
        initial_layout = kb_label.text
    except TimeoutError:
        return KB_ICON_LABEL_NOT_FOUND

    if dry_run:
        if initial_layout == required_layout:
            return Pass()
        else:
            return Fail("Expected keyboard layout \"%s\", but found \"%s\"" %
                        (required_layout, initial_layout))

    current_layout = ""
    while current_layout != initial_layout:
        if current_layout == required_layout:
            break
        kb_label.click()
        current_layout = kb_label.text
    else:
        return Fail("Required keyboard layout \"%s\" not available.")

@handle_act('/luks/keyboard')
def luks_keyboard_handler(element, app_node, local_node):
    luks_keyboard_manipulate(element, app_node, local_node, False)

@handle_chck('/luks/keyboard')
def luks_keyboard_check(element, app_node, local_node):
    return luks_keyboard_manipulate(element, app_node, local_node, True)

