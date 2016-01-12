import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, waiton, getnode, getnodes, getparent, getparents
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr

from dogtail.predicate import GenericPredicate

@handle_action('/installation/hub/partitioning/advanced')
def hub_partitioning_advanced_handler(element, app_node, local_node):
    try:
        manual_label = getnode(app_node, "label", tr("MANUAL PARTITIONING"))
        # advanced partitioning panel is third parent panel of the label
        advanced_panel = getparents(manual_label, "panel")[2]
    except TimeoutError:
        return (False, "Manual partitioning panel not found")
    except IndexError:
        return (False, "Anaconda layout has changed, the anabot needs update")
    default_handler(element, app_node, advanced_panel)
    return True

@handle_action('/installation/hub/partitioning/advanced/schema')
def hub_partitioning_advanced_schema_handler(element, app_node, local_node):
    schemas = {
        'native' : tr("Standard Partition"),
        'btrfs' : tr("Btrfs"),
        'lvm' : tr("LVM"),
        'raid' : tr("RAID"),
        'lvm thinp' : tr("LVM Thin Provisioning")
    }
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
                                  for name in schemas.values()])
        except TimeoutError:
            if not shown:
                group_node.actions['activate'].do()
    if schema_node is None:
        return (False, "Couldn't find combo box for partitioning schema")
    schema_node.click()
    getnode(schema_node, "menu item", schemas[schema]).click()

@handle_action('/installation/hub/partitioning/advanced/select')
def hub_partitioning_advanced_select_handler(element, app_node, local_node):
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
        return [icon.parent.parent
                for icon in getnodes(parent, "icon", visible=None)
                if check(icon)]
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
