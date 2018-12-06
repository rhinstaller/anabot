# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

import fnmatch
import random
import six

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getsibling, disappeared, getnode_scroll
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import NotFoundResult

_local_path = '/installation/hub/syspurpose'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def syspurpose_handler(element, app_node, local_node):
    syspurpose_label = tr("_System Purpose", context="GUI|Spoke")
    try:
        syspurpose = getnode_scroll(app_node, "spoke selector", syspurpose_label)
    except TimeoutError:
        return NotFoundResult(syspurpose_label, where="main hub")
    syspurpose.click()
    try:
        syspurpose_panel = getnode(app_node, "panel", tr("SYSTEM PURPOSE"))
    except TimeoutError:
        return NotFoundResult(tr("SYSTEM PURPOSE") + " SYSTEM PURPOSE spoke")
    default_handler(element, app_node, syspurpose_panel)
    try:
        done_button = getnode(syspurpose_panel, "push button",
                tr("_Done", drop_underscore=False,
                context="GUI|Spoke Navigation"))
    except TimeoutError:
        return NotFoundResult("Done button", where="System Purpose spoke")
    done_button.click()
    return True


@handle_chck('')
@check_action_result
def syspurpose_check(element, app_node, local_node):
    try:
        disappeared(app_node, "panel", tr("SYSTEM PURPOSE"))
        return True
    except TimeoutError:
        return (False, "System purpose spoke is still visible.")


@handle_act('/role')
def role_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    role_name = tr(value)
    panel_name = tr("Role")
    logger.info("searching %s (original %s)", role_name, value)
    try:
        role_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % role_name, where="System purpose panel")
    try:
        role_label = getnode(role_panel_label.parent, "label", role_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % role_name, where="Role selection")
    try:
        role_radio = getsibling(role_label, -1, "radio button")
    except TimeoutError:
        return NotFoundResult("radio button for '%s'" % role_name, where="Role selection")
    if not role_radio.checked:
        role_radio.click()
    return True


@handle_chck('/role')
@check_action_result
def role_check(element, app_node, local_node):
    value = get_attr(element, "value")
    role_name = tr(value)
    panel_name = tr("Role")
    try:
        role_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % panel_name, where="System purpose panel")
    try:
        role_label = getnode(role_panel_label.parent, "label", role_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % role_name, where="Role selection")
    try:
        role_radio = getsibling(role_label, -1, "radio button")
    except TimeoutError:
        return NotFoundResult("radio button for '%s'" % role_name, where="Role selection")
    return role_radio.checked


@handle_act('/sla')
def sla_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    sla_name = tr(value)
    panel_name = tr("Red Hat Service Level Agreement")
    try:
        sla_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % panel_name, where="System purpose panel")
    try:
        sla_label = getnode(sla_panel_label.parent, "label", sla_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % sla_name, where="SLA selection")
    try:
        sla_radio = getsibling(sla_label, -1, "radio button")
    except TimeoutError:
        return NotFoundResult("radio button for '%s'" % sla_name, where="SLA selection")
    if not sla_radio.checked:
        sla_radio.click()
    return True


@handle_chck('/sla')
@check_action_result
def sla_check(element, app_node, local_node):
    value = get_attr(element, "value")
    sla_name = tr(value)
    panel_name = tr("Red Hat Service Level Agreement")
    try:
        sla_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % panel_name, where="System purpose panel")
    try:
        sla_label = getnode(sla_panel_label.parent, "label", sla_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % sla_name, where="SLA selection")
    try:
        sla_radio = getsibling(sla_label, -1, "radio button")
    except TimeoutError:
        return NotFoundResult("radio button for '%s'" % sla_name, where="SLA selection")
    return sla_radio.checked


@handle_act('/usage')
def usage_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    usage_name = tr(value)
    panel_name = tr("Usage")
    try:
        usage_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % panel_name, where="System purpose panel")
    try:
        usage_label = getnode(usage_panel_label.parent, "label", usage_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % usage_name, where="SLA selection")
    try:
        usage_radio = getsibling(usage_label, -1, "radio button")
    except TimeoutError:
        return NotFoundResult("radio button for '%s'" % usage_name, where="SLA selection")
    if not usage_radio.checked:
        usage_radio.click()
    return True


@handle_chck('/usage')
@check_action_result
def usage_check(element, app_node, local_node):
    value = get_attr(element, "value")
    usage_name = tr(value)
    panel_name = tr("Usage")
    try:
        usage_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % panel_name, where="System purpose panel")
    try:
        usage_label = getnode(usage_panel_label.parent, "label", usage_name)
    except TimeoutError:
        return NotFoundResult("label '%s'" % usage_name, where="SLA selection")
    try:
        usage_radio = getsibling(usage_label, -1, "radio button")
    except TimeoutError:
        return NotFoundResult("radio button for '%s'" % usage_name, where="SLA selection")
    return usage_radio.checked
