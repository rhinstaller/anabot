# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, waiton, getnode, getnodes, getparent, getsibling
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.installation.hub.partitioning.advanced.common import schema_name

from dogtail.predicate import GenericPredicate # pylint: disable=import-error

import anabot.runtime.installation.hub.partitioning.advanced.details

_local_path = '/installation/hub/partitioning/advanced'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

_current_selection = None

def check_partitioning_error(app_node):
    try:
        error_bar = getnode(app_node, "info bar", tr("Error"))
        warn_icon = getnode(error_bar, "icon", tr("Warnings"))
        warn_text = getsibling(warn_icon, 1, "label")
        return (False, warn_text.text)
    except TimeoutError:
        return True

@handle_act('')
def base_handler(element, app_node, local_node):
    try:
        manual_label = getnode(app_node, "label", tr("MANUAL PARTITIONING"))
        # advanced partitioning panel is second child of filler which
        # is first parent of MANUAL PARTITIONING label
        advanced_panel = getparent(manual_label, "filler").children[1]
    except TimeoutError:
        return (False, "Manual partitioning panel not found")
    except IndexError:
        return (False, "Anaconda layout has changed, the anabot needs update")
    default_handler(element, app_node, advanced_panel)
    return True

@handle_act('/schema')
def schema_handler(element, app_node, local_node):
    schema = get_attr(element, "value")
    schema_node = None
    group_nodes = getnodes(local_node, "toggle button")
    for group_node in group_nodes:
        shown = True
        if not group_node.checked:
            shown = False
            group_node.actions['activate'].do()
        try:
            schema_node = waiton(group_node,
                                 [GenericPredicate(roleName="combo box",
                                                   name=name)
                                  for name in schema_name()])
        except TimeoutError:
            if not shown:
                group_node.actions['activate'].do()
    if schema_node is None:
        return (False, "Couldn't find combo box for partitioning schema")
    schema_node.click()
    getnode(schema_node, "menu item", schema_name(schema)).click()

@handle_act('/select')
def select_handler(element, app_node, local_node):
    global _current_selection
    def devs(parent, device=None, mountpoint=None):
        def dname(icon):
            return icon.parent.children[0].name
        def mpoint(icon):
            return icon.parent.children[3].name
        def check(icon):
            matches = True
            if device is not None:
                matches = fnmatchcase(dname(icon), device)
            if matches and mountpoint is not None:
                matches = fnmatchcase(mpoint(icon), mountpoint)
            return matches
        try:
            return [icon.parent.parent
                    for icon in getnodes(parent, "icon", visible=None)
                    if check(icon)]
        except TimeoutError:
            return []
    def devname(device_panel):
        return getnode(device_panel, "label", visible=None).name
    fndevice = get_attr(element, "device", None)
    mountpoint = get_attr(element, "mountpoint", None)
    processed = []
    done = False
    _current_selection = None
    while not done:
        done = True
        for device in devs(local_node, fndevice, mountpoint):
            name = devname(device)
            if name not in processed:
                group_node = None
                if not device.showing:
                    group_node = getparent(device, "toggle button")
                    group_node.click()
                _current_selection = device
                device.click()
                default_handler(element, app_node, local_node)
                processed.append(name)
                done = False
                break
    return True

@handle_chck('/select')
def select_check(element, app_node, local_node):
    logger.warning("I have no idea how to implement check for select ATM")
    logger.debug("Check for select is using just result of action itself")
    return action_result(element)

@handle_act('/remove')
@handle_act('/select/remove')
def remove_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept")
    remove_button = getnode(local_node, "push button",
                            tr("Remove", context="GUI|Custom Partitioning"))
    remove_button.click()
    remove_dialog_context = "GUI|Custom Partitioning|Confirm Delete Dialog"
    if dialog_action == "no dialog":
        return
    elif dialog_action == "accept":
        button_text = tr("_Delete It", context=remove_dialog_context)
    elif dialog_action == "reject":
        button_text = tr("_Cancel", context=remove_dialog_context)
    else:
        return (False, "Undefined state")
    dialog_text = tr("Are you sure you want to delete all of the data on %s?")
    dialog_text %= "*"
    dialog_text = unicode(dialog_text)
    try:
        remove_dialog = getnode(app_node, "dialog")
    except:
        return (False, "No dialog appeared after pressing remove button")
    if len([ x for x in getnodes(remove_dialog, "label")
             if fnmatchcase(unicode(x.name), dialog_text)]) != 1:
        return (False, "Different dialog appeared after pressing remove button")
    default_handler(element, app_node, remove_dialog)
    getnode(remove_dialog, "push button", button_text).click()

@handle_chck('/remove')
@handle_chck('/select/remove')
def remove_check(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept")
    logger.debug("Is device dead?: %s", _current_selection.dead)
    logger.debug("Is device showing?: %s", _current_selection.showing)
    if dialog_action in ("no dialog", "accept"):
        return _current_selection.dead and not _current_selection.showing
    elif dialog_action == "reject":
        return not _current_selection.dead and _current_selection.showing
    return (False, "Undefined state")

def remove_related_handler_manipulate(element, app_node, local_node, dry_run):
    check = get_attr(element, "value", "yes") == "yes"
    checkbox_text = tr("Delete _all other file systems in the %s root as well.",
                       context="GUI|Custom Partitioning|Confirm Delete Dialog")
    checkbox_text %= "*"
    checkbox_text = unicode(checkbox_text)
    checkboxes = [x for x in getnodes(local_node, "check box")
                  if fnmatchcase(unicode(x.name), checkbox_text)]
    logger.warn("Found checkboxes: %s", repr(checkboxes))
    if len(checkboxes) != 1:
        return (False, "No or more checkboxes for removing related partitions found. Check screenshot")
    checkbox = checkboxes[0]
    if dry_run:
        return checkbox.checked == check
    if checkbox.checked != check:
        checkbox.click()

@handle_act('/remove/also_related')
@handle_act('/select/remove/also_related')
def remove_related_handler(element, app_node, local_node):
    remove_related_handler_manipulate(element, app_node, local_node, False)

@handle_chck('/remove/also_related')
@handle_chck('/select/remove/also_related')
def remove_related_check(element, app_node, local_node):
    return remove_related_handler_manipulate(element, app_node, local_node,
                                             True)

@handle_act('/rescan')
def rescan_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept")
    rescan_name = tr("Refresh", context="GUI|Custom Partitioning")
    rescan_button = getnode(local_node, "push button", rescan_name)
    rescan_button.click()
    rescan_dialog = getnode(app_node, "dialog", tr("RESCAN DISKS"))
    default_handler(element, app_node, rescan_dialog)
    context = "GUI|Refresh Dialog|Rescan"
    if dialog_action == "accept":
        button_text = tr("_OK", context=context)
    elif dialog_action == "reject":
        button_text = tr("_Cancel", context=context)
    else:
        return (False, "Undefined state")
    getnode(rescan_dialog, "push button", button_text).click()

@handle_act('/rescan/push_rescan')
def rescan_push_rescan_handler(element, app_node, local_node):
    rescan_text = tr("_Rescan Disks", context="GUI|Refresh Dialog|Rescan")
    rescan_button = getnode(local_node, "push button", rescan_text)
    rescan_button.click()

@handle_chck('/rescan/push_rescan')
def rescan_push_rescan_check(element, app_node, local_node):
    # check that scan was successfull
    pass

@handle_act('/autopart')
def autopart_handler(element, app_node, local_node):
    autopart = getnode(local_node, "push button", tr("_Click here to create them automatically."))
    autopart.click()

@handle_act('/add')
def add_handler(element, app_node, local_node):
    accept = get_attr(element, "dialog", "accept") == "accept"
    add_button = getnode(local_node, "push button",
                         tr("Add", context="GUI|Custom Partitioning"))
    add_button.click()
    add_dialog_label = getnode(app_node, "label", tr("ADD A NEW MOUNT POINT"))
    add_dialog = getparent(add_dialog_label, "dialog")
    default_handler(element, app_node, add_dialog)
    context = "GUI|Custom Partitioning|Add Dialog"
    if accept:
        button_text = "_Add mount point"
    else:
        button_text = "_Cancel"
    button_text = tr(button_text, context=context)
    getnode(add_dialog, "push button", button_text).click()

@handle_chck('/add')
@handle_chck('/autopart')
def partitioning_check(element, app_node, local_node):
    return check_partitioning_error(app_node)

def add_mountpoint_handler_manipulate(element, app_node, local_node, dryrun):
    mountpoint = get_attr(element, "value")
    combo = getnode(local_node, "combo box")
    textfield = getnode(combo, "text")
    if not dryrun:
        textfield.typeText(mountpoint)
    else:
        return textfield.text == mountpoint

@handle_act('/add/mountpoint')
def add_mountpoint_handler(element, app_node, local_node):
    add_mountpoint_handler_manipulate(element, app_node, local_node, False)

@handle_chck('/add/mountpoint')
def add_mountpoint_check(element, app_node, local_node):
    add_mountpoint_handler_manipulate(element, app_node, local_node, True)

def add_size_handler_manipulate(element, app_node, local_node, dryrun):
    size = get_attr(element, "value")
    mountpoint = getnode(local_node, "combo box")
    # textfield for size is next to mountpoint combo box
    textfield = getsibling(mountpoint, 1, "text")
    if not dryrun:
        textfield.typeText(size)
    else:
        return textfield.text == size

@handle_act('/add/size')
def add_size_handler(element, app_node, local_node):
    add_size_handler_manipulate(element, app_node, local_node, False)

@handle_chck('/add/size')
def add_size_check(element, app_node, local_node):
    add_size_handler_manipulate(element, app_node, local_node, True)

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(local_node.parent, "push button", tr("_Done", False))
    done_button.click()

@handle_act('/summary')
def summary_handler(element, app_node, local_node):
    accept = get_attr(element, "dialog", "accept") == "accept"
    context = "GUI|Summary Dialog"
    if accept:
        button_text = "_Accept Changes"
    else:
        button_text = "_Cancel & Return to Custom Partitioning"
    button_text = tr(button_text, context=context)
    dialog = getnode(app_node, "dialog", tr("SUMMARY OF CHANGES"))
    dialog_button = getnode(dialog, "push button", button_text)
    dialog_button.click()
