# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getnodes, getparent, getsibling, hold_key, release_key
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.installation.hub.partitioning.advanced.common import schema_name

_local_path = '/installation/hub/partitioning/advanced/details'
_local_select_path = '/installation/hub/partitioning/advanced/select/details'
def handle_act(path):
    handle_action(_local_path + path)
    return handle_action(_local_select_path + path)

def handle_chck(path):
    handle_check(_local_path + path)
    return handle_check(_local_select_path + path)

@handle_act('')
def details_handler(element, app_node, local_node):
    details_node = getnode(local_node, "page tab list")
    details_node = getnodes(details_node, "page tab", sensitive=None)[0]
    default_handler(element, app_node, details_node)

@handle_act('/mountpoint')
def details_mountpoint_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    mountpoint_label = getnode(local_node, "label", tr("Mount _Point:"))
    mountpoint = getsibling(mountpoint_label, 1, "text")
    mountpoint.typeText(value)

@handle_act('/filesystem')
def details_filesystem_handler(element, app_node, local_node):
    fstype = get_attr(element, "select")
    filesystem_label = getnode(local_node, "label", tr("File S_ystem:", context="GUI|Custom Partitioning|Configure"))
    filesystem = getsibling(filesystem_label, 1, "combo box")
    filesystem.click()
    getnode(filesystem, "menu item", fstype).click()

@handle_act('/size')
def details_size_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    size_label = getnode(local_node, "label", tr("_Desired Capacity:"))
    size = getsibling(size_label, 1, "text")
    size.typeText(value)

@handle_act('/name')
def details_name_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    name_label = getnode(local_node, "label", tr("_Name:", context="GUI|Custom Partitioning|Container Dialog"))
    name = getsibling(name_label, 1, "text")
    name.typeText(value)

@handle_act('/label')
def details_label_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    label_label = getnode(local_node, "label", tr("_Label:"))
    label = getsibling(label_label, 1, "text")
    label.typeText(value)

@handle_act('/device_type')
def details_device_type_handler(element, app_node, local_node):
    dev_type = get_attr(element, "select")
    device_type_label = getnode(local_node, "label", tr("Device _Type:", context="GUI|Custom Partitioning|Configure"))
    device_type = getsibling(device_type_label, 1, "combo box")
    device_type.click()
    getnode(device_type, "menu item", schema_name(dev_type)).click()

@handle_act('/devices')
def details_devices_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept")
    devices_label = getnode(local_node, "label", tr("Device(s):"))
    devices_button = getsibling(devices_label, 1, "push button")
    devices_button.click()
    dialog_label = getnode(app_node, "label", tr("CONFIGURE MOUNT POINT"))
    dialog = getparent(dialog_label, "dialog")
    default_handler(element, app_node, dialog)
    context = "GUI|Custom Partitioning|Configure Dialog"
    if dialog_action == "accept":
        button_text = tr("_Select", context=context)
    elif dialog_action == "reject":
        button_text = tr("_Cancel", context=context)
    else:
        return (False, "Undefined state")
    getnode(dialog, "push button", button_text).click()

@handle_act('/devices/deselect')
def details_devices_deselect_handler(element, app_node, local_node):
    name = unicode(get_attr(element, "device"))
    table_cells = getnodes(local_node, "table cell")
    # device is second cell in row consisting of 4 cells, so take only
    # those whose index matches rule: i modulo 4 == 1
    devices = [table_cells[i] for i in xrange(len(table_cells)) if i % 4 == 1]
    logger.info("found devices: %s", repr(devices))
    deselect = [device for device in devices if
                fnmatchcase(unicode(device.name), name)]
    logger.info("Deselecting devices: %s", repr(deselect))
    hold_key('control')
    for device in deselect:
        logger.debug("Deselecting %s", device.name)
        if device.selected:
            device.click()
    release_key('control')

@handle_act('/devices/select')
def details_devices_select_handler(element, app_node, local_node):
    name = unicode(get_attr(element, "device"))
    table_cells = getnodes(local_node, "table cell")
    # device is second cell in row consisting of 4 cells, so take only
    # those whose index matches rule: i modulo 4 == 1
    devices = [table_cells[i] for i in xrange(len(table_cells)) if i % 4 == 1]
    logger.info("found devices: %s", repr(devices))
    select = [device for device in devices if
                fnmatchcase(unicode(device.name), name)]
    hold_key('control')
    for device in select:
        logger.debug("Selecting %s", device.name)
        if not device.selected:
            device.click()
    release_key('control')

@handle_act('/update')
def details_update_handler(element, app_node, local_node):
    try:
        getnode(local_node, "push button", tr("_Update Settings")).click()
    except TimeoutError:
        return False
    return True

@handle_act('/new_volume_group')
def details_new_volume_group(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept")
    # Volume Group is not translated, file bug!
    volume_group_label = getnode(local_node, "label", "Volume Group")
    volume_group_combo = getsibling(volume_group_label, 1, "combo box")
    volume_group_combo.click()
    # Vyvořit nový volume group ... in czech, file bug!
    create_text = tr("Create a new %(container_type)s ...", False) % {
        "container_type" : "volume group"
    }
    selection_window = getnode(app_node, "window")
    new_volgroup = getnode(selection_window, "menu item", create_text)
    new_volgroup.click()
    # dialog appears
    vg_dialog = getnode(app_node, "dialog")
    default_handler(element, app_node, vg_dialog)
    context = "GUI|Custom Partitioning|Container Dialog"
    if dialog_action == "accept":
        button_text = "_Save"
    elif dialog_action == "reject":
        button_text = "_Cancel"
    else:
        return (False, "Undefined state")
    button_text = tr(button_text, context=context)
    getnode(vg_dialog, "push button", button_text).click()
