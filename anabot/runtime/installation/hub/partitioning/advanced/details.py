# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()
import six

from fnmatch import fnmatchcase
from re import match

from anabot.conditions import is_distro_version_ge
from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, handle_step
from anabot.runtime.functions import get_attr, getnode, getnodes, getparent, getparents, getsibling, hold_key, press_key, release_key, clear_text
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.installation.hub.partitioning.advanced.common import schema_name, raid_name, check_partitioning_error
from anabot.runtime.actionresult import NotFoundResult as NotFound, ActionResultPass as Pass,\
    ActionResultFail as Fail
from anabot.variables import set_variable

_local_path = '/installation/hub/partitioning/advanced/details'
_local_select_path = '/installation/hub/partitioning/advanced/select/details'
def handle_act(path):
    def decorator(func):
        handle_action(_local_path + path, func)
        return handle_action(_local_select_path + path, func)
    return decorator

def handle_chck(path):
    def decorator(func):
        handle_check(_local_path + path, func)
        return handle_check(_local_select_path + path, func)
    return decorator

@handle_act('')
def base_handler(element, app_node, local_node):
    details_node = getnode(local_node, "page tab list")
    details_node = getnodes(details_node, "page tab", sensitive=None)[0]
    # local_node may become invalid (e. g. after LUKS device unlock), thus we need to
    # check it's valid for every invoked handler/check and potentially find a new one;
    # default_handler() can't be used here because it won't handle such a change properly
    for child in element.xpathEval("./*"):
        handle_step(child, app_node, local_node)
        if not details_node.visible:
            details_node = getnodes(details_node, "page tab", sensitive=None)[0]
    return True

@handle_chck('')
def base_check(element, app_node, local_node):
    # nothing to check here
    return True

@handle_act('/mountpoint')
def mountpoint_handler(element, app_node, local_node):
    reporter.log_info("Changing mountpoint inside select (<select> <select />) may result in unexpected behavior!")
    value = get_attr(element, "value")
    mountpoint_label = getnode(local_node, "label", tr("Mount _Point:"))
    mountpoint = getsibling(mountpoint_label, 1, "text")
    mountpoint.typeText(value)

@handle_chck('/mountpoint')
def mountpoint_check(element, app_node, local_node):
    value = get_attr(element, "value")
    mountpoint_label = getnode(local_node, "label", tr("Mount _Point:"))
    mountpoint = getsibling(mountpoint_label, 1, "text")
    if mountpoint.text == value:
        return True
    return (False, u"Mountpoint doesn't match, expected: '%s', found: '%s'" % (value, mountpoint.text))

@handle_act('/filesystem')
def filesystem_handler(element, app_node, local_node):
    fstype = get_attr(element, "select")
    filesystem_label = getnode(local_node, "label", tr("File S_ystem:", context="GUI|Custom Partitioning|Configure"))
    filesystem = getsibling(filesystem_label, 1, "combo box")
    filesystem.click()
    try:
        getnode(filesystem, "menu item", fstype).click()
    except TimeoutError:
        press_key('esc')
        return (False, u"Filesystem type '%s' not found" % fstype)

@handle_chck('/filesystem')
def filesystem_check(element, app_node, local_node):
    fstype = get_attr(element, "select")
    filesystem_label = getnode(local_node, "label", tr("File S_ystem:", context="GUI|Custom Partitioning|Configure"))
    filesystem = getsibling(filesystem_label, 1, "combo box")
    if filesystem.name == fstype:
        return True
    return (False, u"Filesystem type doesn't match, expected: '%s', found: '%s'" % (fstype, filesystem.name))

@handle_act('/size')
def size_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    size_label = getnode(local_node, "label", tr("_Desired Capacity:"))
    size = getsibling(size_label, 1, "text")
    size.typeText(value)

@handle_chck('/size')
def size_check(element, app_node, local_node):
    value = get_attr(element, "value")
    size_label = getnode(local_node, "label", tr("_Desired Capacity:"))
    size = getsibling(size_label, 1, "text")
    if size.text == value:
        return True
    return (False, u"Size doesn't match, expected: '%s' found: '%s'" % (value, size.text))

@handle_act('/reformat')
def reformat_handler(element, app_node, local_node):
    action = get_attr(element, "action", "check") == "check"
    reformat = getnode(local_node, "check box", tr("Ref_ormat", context="GUI|Custom Partitioning|Configure"))
    if action != reformat.checked:
        reformat.click()

@handle_chck('/reformat')
def reformat_check(element, app_node, local_node):
    action = get_attr(element, "action", "check") == "check"
    reformat = getnode(local_node, "check box", tr("Ref_ormat", context="GUI|Custom Partitioning|Configure"))
    return action == reformat.checked

@handle_act('/name')
def name_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    name_label = getnode(local_node, "label", tr("_Name:", context="GUI|Custom Partitioning|Container Dialog"))
    name = getsibling(name_label, 1, "text")
    name.typeText(value)

@handle_act('/label')
def label_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    label_label = getnode(local_node, "label", tr("_Label:"))
    label = getsibling(label_label, 1, "text")
    label.typeText(value)

@handle_chck('/label')
def label_check(element, app_node, local_node):
    value = get_attr(element, "value")
    label_label = getnode(local_node, "label", tr("_Label:"))
    label = getsibling(label_label, 1, "text")
    if label.text == value:
        return True
    return (False, u"Label doesn't match, expected: '%s', found: '%s'" % (value, label.text))

@handle_act('/device_type')
def device_type_handler(element, app_node, local_node):
    dev_type = get_attr(element, "select")
    device_type_label = getnode(local_node, "label", tr("Device _Type:", context="GUI|Custom Partitioning|Configure"))
    device_type = getsibling(device_type_label, 1, "combo box")
    device_type.click()
    try:
        getnode(device_type, "menu item", schema_name(dev_type)).click()
    except TimeoutError:
        press_key('esc')
        return (False, u"Device type '%s' not found" % dev_type)

@handle_chck('/device_type')
def device_type_check(element, app_node, local_node):
    dev_type = get_attr(element, "select")
    device_type_label = getnode(local_node, "label", tr("Device _Type:", context="GUI|Custom Partitioning|Configure"))
    device_type = getsibling(device_type_label, 1, "combo box")
    if device_type.name == schema_name(dev_type):
        return True
    return (False, u"Device type doesn't match, expected: '%s', found: '%s'" % (schema_name(dev_type), device_type.name))

@handle_act('/devices')
def devices_handler(element, app_node, local_node):
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
def devices_deselect_handler(element, app_node, local_node):
    name = six.u(get_attr(element, "device"))
    table_cells = getnodes(local_node, "table cell")
    # device is second cell in row consisting of 4 cells, so take only
    # those whose index matches rule: i modulo 4 == 1
    devices = [table_cells[i] for i in range(len(table_cells)) if i % 4 == 1]
    logger.info("found devices: %s", repr(devices))
    deselect = [device for device in devices if
                fnmatchcase(six.u(device.name), name)]
    logger.info("Deselecting devices: %s", repr(deselect))
    hold_key('control')
    for device in deselect:
        logger.debug("Deselecting %s", device.name)
        if device.selected:
            device.click()
    release_key('control')

@handle_act('/devices/select')
def devices_select_handler(element, app_node, local_node):
    name = six.u(get_attr(element, "device"))
    table_cells = getnodes(local_node, "table cell")
    # device is second cell in row consisting of 4 cells, so take only
    # those whose index matches rule: i modulo 4 == 1
    devices = [table_cells[i] for i in range(len(table_cells)) if i % 4 == 1]
    logger.info("found devices: %s", repr(devices))
    select = [device for device in devices if
                fnmatchcase(six.u(device.name), name)]
    hold_key('control')
    for device in select:
        logger.debug("Selecting %s", device.name)
        if not device.selected:
            device.click()
    release_key('control')

@handle_act('/luks_unlock')
def unlock_handler(element, app_node, local_node):
    password = get_attr(element, "password")
    try:
        passphrase_label = getnode(local_node, "label", tr("_Passphrase:"))
        passphrase_field = getsibling(passphrase_label, 1, "password text")
    except TimeoutError:
        return NotFound("Passphrase label or input field")
    # It can be also desirable to have a possibility to just click on the Unlock button,
    # having the passphrase already pre-filled, e. g. after unlock & disk rescan.
    if password is not None:
        passphrase_field.typeText(password)
        # 'luks_password' variable is needed to properly setup automatic unlocking via crypttab
        set_variable("luks_password", password)
    try:
        unlock_button = getsibling(passphrase_label, 1, "push button", "Unlock")
    except TimeoutError:
        return NotFound("Unlock button")
    unlock_button.click()
    return Pass()

@handle_chck('/luks_unlock')
def unlock_check(element, app_node, local_node):
    # part of the following code has been borrowed from base handler for
    # /installation/hub/partitioning/advanced
    try:
        manual_label = getnode(app_node, "label", tr("MANUAL PARTITIONING"))
        # advanced partitioning panel is second child of filler which
        # is first parent of MANUAL PARTITIONING label
        advanced_panel = getparent(manual_label, "filler")
    except TimeoutError:
        return Fail("Manual partitioning panel not found")
    except IndexError:
        return Fail("Anaconda layout has changed, Anabot needs update")

    # Unfortunately the UI behaves differently when some partitioning has already been done
    # (the first partition in the list will be selected instead) vs. when there has been no
    # partitioning for the new system done yet (the right pane will contain details about the
    # unlocked device.
    # The check may not be 100% accurate in the first case.
    try:
        system_label = getnode(advanced_panel, "label", tr("SYSTEM"))
    except TimeoutError:
        system_label = None
    # 1. A 'SYSTEM' label is present, i. e. some partitioning design has already happened
    if system_label:
        logger.debug("Warning: Check for device unlocking may not be 100% accurate")
        try:
            # This approach is a bit crude, but it's likely the best approach we can get -
            # i. e. have a look if there are some 'luks-UUID' labels present
            panel_labels = [n.name for n in getnodes(advanced_panel, "label", visible=None)]
            luks_devices_found = any(map(lambda x: match("luks-([0-9a-f]+-){4}[0-9a-f]+", x), panel_labels))
            if not luks_devices_found:
                return Fail("No 'luks-UUID' devices found, unlocking likely failed.")
        except TimeoutError:
            return Fail("Couldn't find any labels in devices panel, something very unexpected happened.")
    # 2. No new partitioning so far
    else:
        try:
            # We can't use the original 'local_node' as the current one ('page tab') has changed.
            tab_list = getnode(app_node, "page tab list")
            local_node = getnode(tab_list, "page tab", sensitive=None)[0]
            # Unlocking takes a while, so a bigger timeout value is desirable.
            getnode(local_node, "label", tr("LUKS Version:"), 30)
        except TimeoutError:
            return Fail("Partition unlocking failed - couldn't find 'LUKS Version:' label")
    return check_partitioning_error(app_node)

@handle_act('/update')
def update_handler(element, app_node, local_node):
    try:
        getnode(local_node, "push button", tr("_Update Settings")).click()
    except TimeoutError:
        return False
    return True

def volume_group_dialog(element, app_node, local_node):
    local_node = getnode(app_node, "dialog")
    dialog_action = get_attr(element, "dialog", "accept")
    default_handler(element, app_node, local_node)
    context = "GUI|Custom Partitioning|Container Dialog"
    if dialog_action == "accept":
        button_text = "_Save"
    elif dialog_action == "reject":
        button_text = "_Cancel"
    else:
        return (False, "Undefined state")
    button_text = tr(button_text, context=context)
    getnode(local_node, "push button", button_text).click()
    return True

@handle_act('/raid_type')
def raid_type(element, app_node, local_node):
    raid_type = get_attr(element, "select")
    raid_level = raid_name(raid_type)
    try:
        raid_label = getnode(local_node, "label", tr("RAID Level:"))
    except TimeoutError:
        return Fail("Couldn't find 'Raid Level:' label next to raid selection.")
    raid_combo = getsibling(raid_label, 1, "combo box")
    raid_combo.click()
    combo_selection = getnode(app_node, "window")
    try:
        combo_target = getnode(combo_selection, "menu item", raid_level)
    except TimeoutError:
        return Fail("Requested raid level '%s' not found. Was looking for string: '%s'" % (raid_type, raid_level))
    combo_target.click()

@handle_chck('/raid_type')
def raid_type_check(element, app_node, local_node):
    raid_level = raid_name(get_attr(element, "select"), drop_span=False)
    try:
        raid_label = getnode(local_node, "label", tr("RAID Level:"))
    except TimeoutError:
        return Fail("Couldn't find 'Raid Level:' label next to raid selection.")
    raid_combo = getsibling(raid_label, 1, "combo box")
    if raid_level == raid_combo.name:
        return Pass
    else:
        return Fail("Current raid level is: '%s', expected: '%s'" % (raid_combo.name, raid_level))

@handle_act('/new_volume_group')
def new_volume_group(element, app_node, local_node):
    # Volume Group is not translated, file bug!
    volgroup_label_text = "Volume Group"
    if is_distro_version_ge('rhel', 8):
        volgroup_label_text = tr("_Volume Group:", context="GUI|Custom Partitioning|Configure")
    volume_group_label = getnode(local_node, "label", volgroup_label_text)
    volume_group_combo = getsibling(volume_group_label, 1, "combo box")
    volume_group_combo.click()
    # Vyvořit nový volume group ... in czech, file bug!
    create_text = tr("Create a new %(container_type)s ...", False) % {
        "container_type" : "volume group"
    }
    selection_window = getnode(app_node, "window")
    new_volgroup = getnode(selection_window, "menu item", create_text)
    new_volgroup.click()
    return volume_group_dialog(element, app_node, local_node)

@handle_act('/edit_volume_group')
def edit_volume_group(element, app_node, local_node):
    vg_label_text = "Volume Group"
    if is_distro_version_ge('rhel', 8):
        vg_label_text = tr("_Volume Group:", context="GUI|Custom Partitioning|Configure")
    vg_label = getnode(local_node, "label", vg_label_text)
    vg_section = getparents(vg_label, "filler")[2]
    vg_edit_text = tr("_Modify...", context="GUI|Custom Partitioning|Configure")
    vg_edit_button = getnode(vg_section, "push button", vg_edit_text)
    vg_edit_button.click()
    return volume_group_dialog(element, app_node, local_node)

ENCRYPT_CHECKBOX_NOT_FOUND = NotFound("Encrypt checkbox")
@handle_act('/encrypt')
def encrypt_handler(element, app_node, local_node):
    action = get_attr(element, "action")
    try:
        checkbox = getnode(local_node, "check box", tr("Encrypt"))
    except TimeoutError:
        return ENCRYPT_CHECKBOX_NOT_FOUND
    if checkbox.checked != (action == "enable"):
        checkbox.click()

@handle_chck('/encrypt')
def encrypt_check(element, app_node, local_node):
    action = get_attr(element, "action")
    try:
        checkbox = getnode(local_node, "check box", tr("Encrypt"))
    except TimeoutError:
        return ENCRYPT_CHECKBOX_NOT_FOUND
    if checkbox.checked == (action == "enable"):
        return Pass()
    return Fail("Encrypt check box is not in accordance with action '%s'" % action)

def handle_vg_act(path):
    def decorator(func):
        handle_act('/new_volume_group' + path)(func)
        return handle_act('/edit_volume_group' + path)(func)
    return decorator

def handle_vg_chck(path):
    def decorator(func):
        handle_chck('/new_volume_group' + path)(func)
        return handle_chck('/edit_volume_group' + path)(func)
    return decorator

@handle_vg_act('/name')
def vg_name(element, app_node, local_node):
    value = get_attr(element, "value")
    name_label_text = tr("_Name:",
                         context="GUI|Custom Partitioning|Container Dialog")
    name_label = getnode(local_node, "label", name_label_text)
    name = getsibling(name_label, 1, "text")
    name.typeText(value)

@handle_vg_chck('/name')
def vg_name_check(element, app_node, local_node):
    value = get_attr(element, "value")
    name_label_text = tr("_Name:",
                         context="GUI|Custom Partitioning|Container Dialog")
    name_label = getnode(local_node, "label", name_label_text)
    name = getsibling(name_label, 1, "text")
    return name.text == value

@handle_vg_act('/devices')
def vg_devices(element, app_node, local_node):
    devices = getnode(local_node, "table")
    default_handler(element, app_node, devices)

#@handle_vg_act('/devices/select')
#def vg_devices_select(element, app_node, local_node):
#    pass

#@handle_vg_act('/devices/deselect')
#def vg_devices_deselect(element, app_node, local_node):
#    pass

@handle_vg_act('/raid')
def vg_raid_act(element, app_node, local_node):
    raid_level = raid_name(get_attr(element, "select"))
    raid_label = getnode(local_node, "label", tr("RAID Level:"))
    raid_combo = getsibling(raid_label, 1, "combo box")
    raid_combo.click()
    combo_selection = getnode(app_node, "window")
    combo_target = getnode(combo_selection, "menu item", raid_level)
    combo_target.click()

@handle_vg_chck('/raid')
def vg_raid_check(element, app_node, local_node):
    raid_level = raid_name(get_attr(element, "select"))
    raid_label = getnode(local_node, "label", tr("RAID Level:"))
    raid_combo = getsibling(raid_label, 1, "combo box")
    if raid_combo.name == raid_level:
        return Pass()
    return Fail("Selected RAID level '%s' doesn't match expected level '%s'" %
        (raid_combo.name, raid_label))

@handle_vg_act('/encrypt')
def vg_encrypt(element, app_node, local_node):
    value = get_attr(element, "value", "yes")
    checkbox = getnode(local_node, "check box", tr("Encrypt"))
    if checkbox.checked != (value == "yes"):
        checkbox.click()

@handle_vg_chck('/encrypt')
def vg_encrypt_check(element, app_node, local_node):
    value = get_attr(element, "value", "yes")
    checkbox = getnode(local_node, "check box", tr("Encrypt"))
    if (value == "yes") ==  checkbox.checked:
        return True
    return Fail("Unexpected state of VG encryption!")

@handle_vg_act('/luks_version')
def vg_luks_version(element, app_node, local_node):
    version = get_attr(element, "value")
    version_label = getnode(local_node, "label", tr("LUKS Version:"))
    version_combo = getsibling(version_label, 1, "combo box")
    version_combo.click()
    version_menu = getnode(version_combo, "menu item", version)
    version_menu.click()

@handle_vg_chck('/luks_version')
def vg_luks_version_check(element, app_node, local_node):
    version = get_attr(element, "value")
    version_label = getnode(local_node, "label", tr("LUKS Version:"))
    version_combo = getsibling(version_label, 1, "combo box")
    if version_combo.name == version:
        return True
    return Fail("Current LUKS version does not match the requested version: '%s'" % version)

def size_label(app_node, local_node):
    context = "GUI|Custom Partitioning|Container Dialog"
    label_text = tr("Si_ze policy:", context=context)
    return getnode(local_node, "label", label_text)

@handle_vg_act('/size_policy')
def vg_size_policy(element, app_node, local_node):
    policies = {
        "fixed" : tr("Fixed"),
        "maximum" : tr("As large as possible"),
        "auto" : tr("Automatic"),
    }
    policy = policies[get_attr(element, "select")]
    size_policy = getsibling(size_label(app_node, local_node), 1, "combo box")
    size_policy.click()
    combo_selection = getnode(app_node, "window")
    combo_target = getnode(combo_selection, "menu item", policy)
    combo_target.click()

@handle_vg_act('/size')
def vg_size(element, app_node, local_node):
    size = get_attr(element, "value")
    size_value = getsibling(size_label(app_node, local_node), 1, "text")
    size_value.click()
    clear_text(size_value)
    size_value.typeText(size)
