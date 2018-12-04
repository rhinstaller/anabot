# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

import fnmatch
import random
import six

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getnodes, getsibling, combo_scroll, type_text, press_key
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import notfound as notfound_new

def notfound(*args, **kwargs):
    return (False, notfound_new(*args, **kwargs))

_local_path = '/installation/hub/syspurpose'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def syspurpose_handler(element, app_node, local_node):
    syspurpose_label = tr("_System Purpose", context="GUI|Spoke")
    try:
        syspurpose = getnode_scroll(app_node, "spoke selector", syspurpose_label)
    except TimeoutError:
        return notfound(syspurpose_label, where="main hub")
    syspurpose.click()
    try:
        syspurpose_panel = getnode(app_node, "panel", tr("SYSTEM PURPOSE"))
    except TimeoutError:
        return notfound(tr("SYSTEM PURPOSE") + " SYSTEM PURPOSE spoke")
    default_handler(element, app_node, syspurpose_panel)
    try:
        done_button = getnode(syspurpose_panel, "push button",
                tr("_Done", drop_underscore=False,
                context="GUI|Spoke Navigation"))
    except TimeoutError:
        return notfound("Done button", where="System Purpose spoke")
    done_button.click()
    return True


@handle_chck('')
def syspurpose_check(element, app_node, local_node):
    if action_result(element)[0] != False:
        return action_result(element)
    try:
        getnode(app_node, "panel", tr("SYSTEM PURPOSE"), visible=False)
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
        return notfound("label '%s'" % role_name, where="System purpose panel")
    try:
        role_label = getnode(role_panel_label.parent, "label", role_name)
    except TimeoutError:
        return notfound("label '%s'" % role_name, where="Role selection")
    try:
        role_radio = getsibling(role_label, -1, "radio button")
    except TimeoutError:
        return notfound("radio button for '%s'" % role_name, where="Role selection")
    if not role_radio.checked:
        role_radio.click()
    return True


@handle_chck('/role')
def role_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    role_name = tr(value)
    panel_name = tr("Role")
    try:
        role_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return notfound("label '%s'" % panel_name, where="System purpose panel")
    try:
        role_label = getnode(role_panel_label.parent, "label", role_name)
    except TimeoutError:
        return notfound("label '%s'" % role_name, where="Role selection")
    try:
        role_radio = getsibling(role_label, -1, "radio button")
    except TimeoutError:
        return notfound("radio button for '%s'" % role_name, where="Role selection")
    return role_radio.checked


@handle_act('/sla')
def sla_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    sla_name = tr(value)
    panel_name = tr("Red Hat Service Level Agreement")
    try:
        sla_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return notfound("label '%s'" % panel_name, where="System purpose panel")
    try:
        sla_label = getnode(sla_panel_label.parent, "label", sla_name)
    except TimeoutError:
        return notfound("label '%s'" % sla_name, where="SLA selection")
    try:
        sla_radio = getsibling(sla_label, -1, "radio button")
    except TimeoutError:
        return notfound("radio button for '%s'" % sla_name, where="SLA selection")
    if not sla_radio.checked:
        sla_radio.click()
    return True


@handle_chck('/sla')
def sla_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    sla_name = tr(value)
    panel_name = tr("Red Hat Service Level Agreement")
    try:
        sla_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return notfound("label '%s'" % panel_name, where="System purpose panel")
    try:
        sla_label = getnode(sla_panel_label.parent, "label", sla_name)
    except TimeoutError:
        return notfound("label '%s'" % sla_name, where="SLA selection")
    try:
        sla_radio = getsibling(sla_label, -1, "radio button")
    except TimeoutError:
        return notfound("radio button for '%s'" % sla_name, where="SLA selection")
    return sla_radio.checked


@handle_act('/usage')
def usage_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    usage_name = tr(value)
    panel_name = tr("Usage")
    try:
        usage_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return notfound("label '%s'" % panel_name, where="System purpose panel")
    try:
        usage_label = getnode(usage_panel_label.parent, "label", usage_name)
    except TimeoutError:
        return notfound("label '%s'" % usage_name, where="SLA selection")
    try:
        usage_radio = getsibling(usage_label, -1, "radio button")
    except TimeoutError:
        return notfound("radio button for '%s'" % usage_name, where="SLA selection")
    if not usage_radio.checked:
        usage_radio.click()
    return True


@handle_chck('/usage')
def usage_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    usage_name = tr(value)
    panel_name = tr("Usage")
    try:
        usage_panel_label = getnode(local_node, "label", panel_name)
    except TimeoutError:
        return notfound("label '%s'" % panel_name, where="System purpose panel")
    try:
        usage_label = getnode(usage_panel_label.parent, "label", usage_name)
    except TimeoutError:
        return notfound("label '%s'" % usage_name, where="SLA selection")
    try:
        usage_radio = getsibling(usage_label, -1, "radio button")
    except TimeoutError:
        return notfound("radio button for '%s'" % usage_name, where="SLA selection")
    return usage_radio.checked
