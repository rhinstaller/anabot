import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()
import six

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode,\
    getparent, clear_text, getsibling
from anabot.runtime.errors import NonexistentError, TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultPass as Pass, ActionResultFail as Fail
from anabot.variables import set_variable

_local_path = '/installation/hub/partitioning/luks_dialog'
_local_advanced_path = '/installation/hub/partitioning/advanced/luks_dialog'
_hub_path = '/installation/hub/luks_dialog'
def handle_act(path):
    def decorator(func):
        handle_action(_local_path + path, func)
        handle_action(_hub_path + path, func)
        return handle_action(_local_advanced_path + path, func)
    return decorator

def handle_chck(path):
    def decorator(func):
        handle_check(_local_path + path, func)
        handle_check(_hub_path + path, func)
        return handle_check(_local_advanced_path + path, func)
    return decorator

_entered_luks_password = ""
_entered_luks_confirm_password = ""

BLACK_CIRCLE = u'\u25cf'
LUKS_LABEL_NOT_FOUND = NotFound("Disk encryption passphrase label")
LUKS_DIALOG_NOT_FOUND = NotFound("LUKS panel")
@handle_act('')
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

@handle_chck('')
def luks_check(element, app_node, local_node):
    return action_result(element)

PW_LABEL_NOT_FOUND = NotFound("passphrase label")
PW_ENTRY_NOT_FOUND = NotFound("passphrase entry")
def luks_password_manipulate(element, app_node, local_node, dry_run):
    global _entered_luks_password
    value = get_attr(element, "value")
    try:
        pw_label = getnode(local_node, "label",
                           tr("_Passphrase:", context="GUI|Passphrase Dialog"))
    except NonexistentError:
        return PW_LABEL_NOT_FOUND
    try:
        pw_entry = getsibling(pw_label, -1, "password text")
    except NonexistentError:
        return PW_ENTRY_NOT_FOUND
    if not dry_run:
        pw_entry.click()
        clear_text(pw_entry)
        logger.info("Entering LUKS password '%s'" % value)
        pw_entry.typeText(value)
        _entered_luks_password = value
    else:
        if len(value)*BLACK_CIRCLE == six.u(pw_entry.text):
            return Pass()
        else:
            return Fail("LUKS password doesn't have expected length.")

@handle_act('/password')
def luks_password_handler(element, app_node, local_node):
    luks_password_manipulate(element, app_node, local_node, False)

@handle_chck('/password')
def luks_password_check(element, app_node, local_node):
    return luks_password_manipulate(element, app_node, local_node, True)

PW_CONFIRM_LABEL_NOT_FOUND = NotFound("confirmation passphrase label")
PW_CONFIRM_ENTRY_NOT_FOUND = NotFound("confirmation passphrase entry")
def luks_confirm_password_manipulate(element, app_node, local_node, dry_run):
    global _entered_luks_confirm_password
    value = get_attr(element, "value")
    try:
        pw_confirm_label = getnode(local_node, "label",
                                   tr("Con_firm:", context="GUI|Passphrase Dialog"))
    except NonexistentError:
        return PW_CONFIRM_LABEL_NOT_FOUND
    try:
        pw_confirm_entry = getsibling(pw_confirm_label, -1, "password text")
    except NonexistentError:
        return PW_CONFIRM_ENTRY_NOT_FOUND
    if not dry_run:
        pw_confirm_entry.click()
        clear_text(pw_confirm_entry)
        logger.info("Entering LUKS confirmation password '%s'" % value)
        pw_confirm_entry.typeText(value)
        _entered_luks_confirm_password = value
    else:
        if len(value)*BLACK_CIRCLE == six.u(pw_confirm_entry.text):
            return Pass()
        else:
            return Fail("LUKS confirmation password doesn't have expected length.")

@handle_act('/confirm_password')
def luks_confirm_password_handler(element, app_node, local_node):
    luks_confirm_password_manipulate(element, app_node, local_node, False)

@handle_chck('/confirm_password')
@check_action_result
def luks_confirm_password_check(element, app_node, local_node):
    return luks_confirm_password_manipulate(element, app_node, local_node, True)

@handle_act('/cancel')
def luks_cancel_handler(element, app_node, local_node):
    try:
        cancel_button = getnode(local_node, "push button",
                                tr("_Cancel", context="GUI|Passphrase Dialog"))
        cancel_button.click()
    except NonexistentError:
        return NotFound("active \"Cancel\" button")

@handle_chck('/cancel')
@check_action_result
def luks_cancel_check(element, app_node, local_node):
    # The actual check is performed by the check for whole LUKS dialog
    return Pass()

@handle_act('/save')
def luks_save_handler(element, app_node, local_node):
    global _entered_luks_password, _entered_luks_confirm_password
    try:
        save_button = getnode(local_node, "push button",
                              tr("_Save Passphrase", context="GUI|Passphrase Dialog"))
        save_button.click()
    except NonexistentError:
        return NotFound("active \"Save Passphrase\" button")
    if _entered_luks_password == _entered_luks_confirm_password:
        set_variable("luks_password", _entered_luks_password)
        return Pass()
    else:
        return Fail("LUKS password and confirmation password don't match: "
                    " '%s' '%s', but Save button was active" %
                    (_entered_luks_password, _entered_luks_confirm_password))

@handle_chck('/save')
@check_action_result
def luks_save_check(element, app_node, local_node):
    # The actual check is performed by the check for whole LUKS dialog
    return Pass()

KB_PANEL_NOT_FOUND = NotFound("Keyboard Layout panel")
KB_ICON_LABEL_NOT_FOUND = NotFound("keyboard layout icon or label")
def luks_keyboard_manipulate(element, app_node, local_node, dry_run):
    required_layout = get_attr(element, "layout")
    try:
        panel = getnode(local_node, "panel", "Keyboard Layout")
    except NonexistentError:
        return KB_PANEL_NOT_FOUND
    try:
        icon = getnode(panel, "icon")
        kb_label = getsibling(icon, 1, "label")
        initial_layout = kb_label.text
    except NonexistentError:
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

@handle_act('/keyboard')
def luks_keyboard_handler(element, app_node, local_node):
    luks_keyboard_manipulate(element, app_node, local_node, False)

@handle_chck('/keyboard')
def luks_keyboard_check(element, app_node, local_node):
    return luks_keyboard_manipulate(element, app_node, local_node, True)

#TODO: add check and handler for password status message and
#      for password strength indicator, provided it's feasible

