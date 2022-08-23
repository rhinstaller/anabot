# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getsibling
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import NotFoundResult as NotFound, ActionResultPass as Pass, ActionResultFail as Fail
from anabot.variables import set_variable

_local_path = '/installation/hub/partitioning/add_specialized_disk'
def handle_act(path, *args, **kwargs):
    return handle_action(_local_path + path, *args, **kwargs)

def handle_chck(path, *args, **kwargs):
    return handle_check(_local_path + path, *args, **kwargs)

def select_manipulate(element, app_node, local_node, dryrun):
    name = get_attr(element, "names", "*")
    action = get_attr(element, "action", "select")

    try:
        results_label = getnode(app_node, "label", tr("Search Res_ults:", context="GUI|Installation Destination|Filter|Search"))
        table_pane = getsibling(results_label, 1, "scroll pane")
        disks_table = getnode(table_pane, "table")
    except TimeoutError:
        return NotFound("results label, table pane or disks table")

    # There are no relevant cells found if there are no specialized disks:
    try:
        cells = getnodes(disks_table, "table cell")
        column_count = len(getnodes(disks_table, "table column header"))
    except TimeoutError:
        logger.info("No cells for specialized disks found.")
        return Pass()

    # every table row has checkbox on position 0 and device name on 1
    name_cells = [
        c
        for c in cells[1::column_count]
        if fnmatchcase(c.name, name)
    ]
    # we need to know if there are any specialized disks to also select all
    # of the regular disks by default in such a case - see RTT-4385
    if len(name_cells):
        set_variable('specialized_disks_present', '1')
    checkbox_cells = [
        getsibling(c, -1, "table cell")
        for c in name_cells
    ]
    logger.info("Devices that match name '%s' found: '%s'" % (name, [n.name for n in name_cells]))
    for c in checkbox_cells:
        device_name = getsibling(c, 1).name
        if (action == "select") != (c.checked):
            if dryrun:
                return Fail("Checkbox status for device '%s' doesn't match required action '%s'" % (device_name, action))
            logger.info("Going to click on checkbox for device '%s'" % device_name)
            c.click()
    return Pass()

@handle_act('/select')
def select_handler(element, app_node, local_node):
    return select_manipulate(element, app_node, local_node, False)

@handle_chck('/select')
def select_check(element, app_node, local_node):
    return select_manipulate(element, app_node, local_node, True)

@handle_act('/done')
def done_handler(element, app_node, local_node):
    try:
        done_button = getnode(app_node, "push button", tr("_Done", drop_underscore=False, context="GUI|Spoke Navigation"))
    except TimeoutError:
        return NotFound("clickable Done button")
    done_button.click()
    return Pass()

@handle_chck('/done')
@check_action_result
def done_check(element, app_node, local_node):
    return Pass()
