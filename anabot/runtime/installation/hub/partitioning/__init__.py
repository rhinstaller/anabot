import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getnodes
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr

# submodules
from . import advanced

@handle_action('/installation/hub/partitioning')
def hub_partitioning_handler(element, app_node, local_node):
    partitioning = getnode(app_node, "spoke selector",
                           tr("INSTALLATION DESTINATION"))
    partitioning.click()
    partitioning_panel = getnode(app_node, "panel",
                                 tr("INSTALLATION DESTINATION"))
    default_handler(element, app_node, partitioning_panel)

@handle_action('/installation/hub/partitioning/disk')
def hub_partitioning_handler_disk(element, app_node, local_node):
    name = get_attr(element, "name")
    action = get_attr(element, "action", "select")
    disks = getnodes(local_node, node_type="disk overview")
    disks = [disk for disk in disks
             if fnmatchcase(disk.children[0].children[3].text, name)]
    for disk in disks:
        # selected disk has icon without name
        icon = getnode(disk, node_type="icon")
        if action == "select" and not disk.name != "":
            disk.click()
        elif action == "deselect" and icon.name == "":
            disk.click()

@handle_action('/installation/hub/partitioning/mode')
def hub_partitioning_handler_mode(element, app_node, local_node):
    mode = get_attr(element, "mode")
    if mode == "default":
        return
    if mode == "automatic":
        radio_text = tr("A_utomatically configure partitioning.")
    if mode == "manual":
        radio_text = tr("_I will configure partitioning.")
    radio = getnode(local_node, "radio button", radio_text)
    if not radio.checked:
        radio.click()

@handle_action('/installation/hub/partitioning/additional_space')
def hub_partitioning_handler_additional_space(element, app_node, local_node):
    action = get_attr(element, "action", "enable")
    checkbox_text = tr("I would like to _make additional space available.")
    additional_checkbox = getnode(local_node, "check box", checkbox_text)
    if (action == "enable") != additional_checkbox.checked:
        additional_checkbox.click()

@handle_action('/installation/hub/partitioning/done')
def hub_partitioning_handler_done(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()

@handle_action('/installation/hub/partitioning/reclaim')
def hub_partitioning_handler_reclaim(element, app_node, local_node):
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

@handle_action('/installation/hub/partitioning/reclaim/delete_all')
def hub_partitioning_handler_reclaim_delete_all(element, app_node, local_node):
    delete_all_button = getnode(local_node, "push button",
                                tr("Delete _all", context="GUI|Reclaim Dialog"))
    delete_all_button.click()
