import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getnode_scroll, scrollto,\
    getparent, clear_text, getsibling
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.variables import get_variable
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultPass as Pass, ActionResultFail as Fail
from anabot.variables import set_variable, get_variable

# submodules
from . import advanced

_local_path = '/installation/hub/partitioning'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    partitioning_label = tr("INSTALLATION _DESTINATION", context="GUI|Spoke")
    partitioning = getnode_scroll(app_node, "spoke selector",
                                  partitioning_label)
    partitioning.click()
    partitioning_panel = getnode(app_node, "panel",
                                 tr("INSTALLATION DESTINATION"))
    default_handler(element, app_node, partitioning_panel)

@handle_chck('')
def base_check(element, app_node, local_node):
    try:
        getnode(app_node, "panel", tr("INSTALLATION DESTINATION"))
        return (False, "Installation destination panel is still visible.")
    except TimeoutError:
        pass
    partitioning_label = tr("INSTALLATION _DESTINATION", context="GUI|Spoke")
    partitioning = getnode(app_node, "spoke selector", partitioning_label,
                           visible=None)
    try:
        getnode(partitioning, "label",
                tr("Error checking storage configuration"), visible=None)
        return (False, "Error checking storage configuration")
    except TimeoutError:
        pass
    return True

# Anaconda doesn't provide enough information for ATK about disk selection
# so we need to remember the disk selection ourself.
__disk_selection = {}
def disk_manipulate(element, app_node, local_node, dryrun):
    def disk_name(node):
        return node.children[0].children[3].text
    name = get_attr(element, "name")
    action = get_attr(element, "action", "select")
    disks = getnodes(local_node, node_type="disk overview", visible=None)
    # Expected behaviour is, that when there is only one disk, it's selected.
    # When there are more disks, they are not selected.
    # This doesn't apply for interactive kickstart installation where all
    # disks are always selected. Maybe there's different behaviour while
    # ignoring drives.
    if len(__disk_selection) == 0:
        d_names = [disk_name(d) for d in disks]
        logger.debug("Found disks: %s", ",".join(d_names))
        if len(d_names) == 1 or get_variable('interactive_kickstart', '0') == '1':
            for d_name in d_names:
                __disk_selection[d_name] = True
        else:
            for d_name in d_names:
                __disk_selection[d_name] = False
    # Filter those, that match name attribute
    disks = [disk for disk in disks if fnmatchcase(disk_name(disk), name)]
    logger.debug("Filtered disks: %s", ",".join([disk_name(d) for d in disks]))
    for disk in disks:
        if dryrun:
            # report warning
            reporter.log_info("Checking disk selection doesn't work at the moment due to https://bugzilla.redhat.com/show_bug.cgi?id=1353850")
            return True
        else:
            logger.debug("Selecting/deselecting disk: %s", disk_name(disk))
            if action == "select" and not __disk_selection[disk_name(disk)]:
                logger.debug("Clicking on disk %s.", disk_name(disk))
                scrollto(disk)
                disk.click()
                __disk_selection[disk_name(disk)] = True
            elif action == "deselect" and __disk_selection[disk_name(disk)]:
                logger.debug("Clicking on disk %s.", disk_name(disk))
                scrollto(disk)
                disk.click()
                __disk_selection[disk_name(disk)] = False
    if dryrun:
        return True

@handle_act('/disk')
def disk_handler(element, app_node, local_node):
    disk_manipulate(element, app_node, local_node, False)

@handle_chck('/disk')
def disk_check(element, app_node, local_node):
    return disk_manipulate(element, app_node, local_node, True)

def mode_manipulate(element, app_node, local_node, dryrun):
    mode = get_attr(element, "mode")
    if mode == "default":
        return
    if mode == "automatic":
        radio_text = tr("A_utomatically configure partitioning.")
    if mode == "manual":
        radio_text = tr("_I will configure partitioning.")
    radio = getnode_scroll(local_node, "radio button", radio_text)
    if dryrun:
        return radio.checked
    if not radio.checked:
        radio.click()

@handle_act('/mode')
def mode_handler(element, app_node, local_node):
    mode_manipulate(element, app_node, local_node, False)

@handle_chck('/mode')
def mode_check(element, app_node, local_node):
    return mode_manipulate(element, app_node, local_node, True)

def additional_space_manipulate(element, app_node, local_node, dry_run):
    action = get_attr(element, "action", "enable")
    checkbox_text = tr("I would like to _make additional space available.")
    additional_checkbox = getnode_scroll(local_node, "check box", checkbox_text)
    if not dry_run:
        if (action == "enable") != additional_checkbox.checked:
            additional_checkbox.click()
    else:
        return (action == "enable") == additional_checkbox.checked

@handle_act('/additional_space')
def additional_space_handler(element, app_node, local_node):
    additional_space_manipulate(element, app_node, local_node, False)

@handle_chck('/additional_space')
def additional_space_check(element, app_node, local_node):
    return additional_space_manipulate(element, app_node, local_node, True)

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()
    return True

@handle_chck('/done')
@check_action_result
def done_check(element, app_node, local_node):
    try:
        warning_bar = getnode(local_node, 'info bar', tr('Warnings'))
        return (False, "Error occured")
    except TimeoutError:
        return True

@handle_act('/reclaim')
def reclaim_handler(element, app_node, local_node):
    # TODO action=reclaim/cancel
    reclaim_dialog = None
    for dialog in getnodes(app_node, "dialog"):
        try:
            getnode(dialog, "label", tr("RECLAIM DISK SPACE"))
            reclaim_dialog = dialog
        except TimeoutError:
            pass
    if reclaim_dialog is None:
        return (False, "Reclaim dialog not found")
    default_handler(element, app_node, reclaim_dialog)
    reclaim_button = getnode(reclaim_dialog, "push button",
                             tr("_Reclaim space", context="GUI|Reclaim Dialog"))
    reclaim_button.click()
    return True

@handle_chck('/reclaim')
def reclaim_check(element, app_node, local_node):
    return action_result(element)

@handle_act('/reclaim/delete_all')
def reclaim_delete_all_handler(element, app_node, local_node):
    try:
        delete_all_button = getnode(local_node, "push button",
                                    tr("Delete _all", context="GUI|Reclaim Dialog"))
    except TimeoutError:
        return (False, 'Didn\'t find "Delete all" button.')
    delete_all_button.click()
    return True

@handle_chck('/reclaim/delete_all')
def reclaim_delete_all_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    table = getnode(local_node, "tree table")
    counter = -1
    free_space = tr("Free space")
    for cell in getnodes(table, "table cell", visible=None):
        counter += 1
        if counter % 5 == 0:
            part_label = cell.text
        if counter % 5 == 4 and part_label != free_space and cell.text != tr("Delete"):
            return (False, "Not all disks/partitions are scheduled to be deleted")
    return True


def encrypt_data_manipulate(element, app_node, local_node, dry_run):
    action = get_attr(element, "action", "enable")
    checkbox_text = tr("_Encrypt my data.")
    encrypt_checkbox = getnode_scroll(local_node, "check box", checkbox_text)
    if not dry_run:
        if ((action == "enable") != encrypt_checkbox.checked or
                (action == "disable") == encrypt_checkbox.checked):
            encrypt_checkbox.click()
    else:
        if ((action == "enable") == encrypt_checkbox.checked or
                (action == "disable") != encrypt_checkbox.checked):
            return Pass()
        else:
            return Fail("Data encryption checkbox state doesn't correspond "
                        "with required state \"%s\"" % action)

@handle_act('/encrypt_data')
def encrypt_data_handler(element, app_node, local_node):
    encrypt_data_manipulate(element, app_node, local_node, False)

@handle_chck('/encrypt_data')
def encrypt_data_check(element, app_node, local_node):
    return encrypt_data_manipulate(element, app_node, local_node, True)

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

