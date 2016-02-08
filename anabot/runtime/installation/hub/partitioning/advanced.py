import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, waiton, getnode, getnodes, getparent, getparents, getsibling, hold_key, release_key
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr

from dogtail.predicate import GenericPredicate

_local_path = '/installation/hub/partitioning/advanced'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

def schema_name(schema=None):
    SCHEMAS = {
        'native' : tr("Standard Partition"),
        'btrfs' : tr("Btrfs"),
        'lvm' : tr("LVM"),
        'raid' : tr("RAID"),
        'lvm thinp' : tr("LVM Thin Provisioning")
    }
    if schema is not None:
        return SCHEMAS[schema]
    return SCHEMAS.values()

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
    while not done:
        done = True
        for device in devs(local_node, fndevice, mountpoint):
            name = devname(device)
            if name not in processed:
                group_node = None
                if not device.showing:
                    group_node = getparent(device, "toggle button")
                    group_node.click()
                device.click()
                default_handler(element, app_node, local_node)
                processed.append(name)
                done = False
                break

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

@handle_act('/remove/also_related')
@handle_act('/select/remove/also_related')
def remove_related_handler(element, app_node, local_node):
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
    if checkbox.checked != check:
        checkbox.click()

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

@handle_act('/add/mountpoint')
def add_mountpoint_handler(element, app_node, local_node):
    mountpoint = get_attr(element, "value")
    combo = getnode(local_node, "combo box")
    textfield = getnode(combo, "text")
    textfield.typeText(mountpoint)

@handle_act('/add/size')
def add_size_handler(element, app_node, local_node):
    size = get_attr(element, "value")
    mountpoint = getnode(local_node, "combo box")
    # textfield for size is next to mountpoint combo box
    textfield = getsibling(mountpoint, 1, "text")
    textfield.typeText(size)

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

@handle_act('/details')
@handle_act('/select/details')
def details_handler(element, app_node, local_node):
    details_node = getnode(local_node, "page tab list")
    details_node = getnodes(details_node, "page tab", sensitive=None)[0]
    default_handler(element, app_node, details_node)

@handle_act('/details/mountpoint')
@handle_act('/select/details/mountpoint')
def details_mountpoint_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    mountpoint_label = getnode(local_node, "label", tr("Mount _Point:"))
    mountpoint = getsibling(mountpoint_label, 1, "text")
    mountpoint.typeText(value)

@handle_act('/details/filesystem')
@handle_act('/select/details/filesystem')
def details_filesystem_handler(element, app_node, local_node):
    fstype = get_attr(element, "select")
    filesystem_label = getnode(local_node, "label", tr("File S_ystem:", context="GUI|Custom Partitioning|Configure"))
    filesystem = getsibling(filesystem_label, 1, "combo box")
    filesystem.click()
    getnode(filesystem, "menu item", fstype).click()

@handle_act('/details/size')
@handle_act('/select/details/size')
def details_size_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    size_label = getnode(local_node, "label", tr("_Desired Capacity:"))
    size = getsibling(size_label, 1, "text")
    size.typeText(value)

@handle_act('/details/name')
@handle_act('/select/details/name')
def details_name_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    name_label = getnode(local_node, "label", tr("_Name:", context="GUI|Custom Partitioning|Container Dialog"))
    name = getsibling(name_label, 1, "text")
    name.typeText(value)

@handle_act('/details/label')
@handle_act('/select/details/label')
def details_label_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    label_label = getnode(local_node, "label", tr("_Label:"))
    label = getsibling(label_label, 1, "text")
    label.typeText(value)

@handle_act('/details/device_type')
@handle_act('/select/details/device_type')
def details_device_type_handler(element, app_node, local_node):
    dev_type = get_attr(element, "select")
    device_type_label = getnode(local_node, "label", tr("Device _Type:", context="GUI|Custom Partitioning|Configure"))
    device_type = getsibling(device_type_label, 1, "combo box")
    device_type.click()
    getnode(device_type, "menu item", schema_name(dev_type)).click()

@handle_act('/details/devices')
@handle_act('/select/details/devices')
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

@handle_act('/details/devices/deselect')
@handle_act('/select/details/devices/deselect')
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

@handle_act('/details/devices/select')
@handle_act('/select/details/devices/select')
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

@handle_act('/details/update')
@handle_act('/select/details/update')
def details_update_handler(element, app_node, local_node):
    try:
        getnode(local_node, "push button", tr("_Update Settings")).click()
    except TimeoutError:
        return False
    return True
