import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr

# submodules
from . import advanced

_local_path = '/installation/hub/partitioning'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    partitioning = getnode(app_node, "spoke selector",
                           tr("_INSTALLATION DESTINATION", context="GUI|Spoke"))
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
        return True

def disk_manipulate(element, app_node, local_node, dryrun):
    name = get_attr(element, "name")
    action = get_attr(element, "action", "select")
    disks = getnodes(local_node, node_type="disk overview")
    disks = [disk for disk in disks
             if fnmatchcase(disk.children[0].children[3].text, name)]
    for disk in disks:
        # selected disk has icon without name
        icon = getnode(disk, node_type="icon")
        if action == "select" and icon.name != "":
            if dryrun:
                return False
            else:
                disk.click()
        elif action == "deselect" and icon.name == "":
            if dryrun:
                return False
            else:
                disk.click()
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
    radio = getnode(local_node, "radio button", radio_text)
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
    additional_checkbox = getnode(local_node, "check box", checkbox_text)
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
def done_check(element, app_node, local_node):
    return action_result(element)

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
    if not action_result(element)[0]:
        return action_result(element)
    table = getnode(local_node, "tree table")
    counter = -1
    for cell in getnodes(table, "table cell", visible=None):
        counter += 1
        if counter % 5 == 4 and cell.text != tr("Delete"):
            return (False, "Not all disks/partitions are scheduled to be deleted")
    return True
