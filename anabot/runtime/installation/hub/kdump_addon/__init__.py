# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler
from anabot.runtime.functions import disappeared, getnode, getnode_scroll, getparents
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import NotFoundResult as NotFound, ActionResultFail as Fail
from anabot.runtime.errors import TimeoutError
from anabot.runtime.installation.common import done_handler

_local_path = '/installation/hub/kdump'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def kdump_handler(element, app_node, local_node):
    kdump_selector_label = tr("_KDUMP", context="GUI|Spoke")
    try:
        kdump_selector = getnode_scroll(app_node, "spoke selector", kdump_selector_label)
    except TimeoutError:
        return NotFound(kdump_selector_label, where="main hub")
    kdump_selector.click()
    try:
        kdump_label = getnode(app_node, "label", tr("KDUMP"))
    except TimeoutError:
        return NotFound(tr("KDUMP") + "label", where=" KDUMP spoke")
    try:
        kdump_panel = getparents(kdump_label, "panel")[2]
    except TimeoutError:
        return NotFound(tr("KDUMP") + "panel", where=" KDUMP spoke")

    default_handler(element, app_node, kdump_panel)
    try:
        return done_handler(element, app_node, kdump_panel)
    except TimeoutError:
        return NotFound("Done button", where="KDUMP spoke")

@handle_chck('')
@check_action_result
def kdump_check(element, app_node, local_node):
    try:
        disappeared(app_node, "panel", tr("KDUMP"))
        return True
    except TimeoutError:
        return Fail("KDUMP spoke is still visible.")

@handle_act('/enable')
def kdump_enable_handler(element, app_node, local_node):
    raise NotImplementedError("Kdump spoke functionality has not been implemented yet.")

@handle_chck('/enable')
def kdump_enable_check(element, app_node, local_node):
    return False

@handle_act('/memory_reservation')
def memory_reservation_handler(element, app_node, local_node):
    raise NotImplementedError("Kdump spoke functionality has not been implemented yet.")

@handle_chck('/memory_reservation')
def memory_reservation_check(element, app_node, local_node):
    return False
