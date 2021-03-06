import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from time import sleep


_local_path = '/initial_setup/subscription_manager/sla_panel'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def sla_panel_handler(element, app_node, local_node):
    sla_panel = local_node
    try:
        sla_label = getnode(local_node, 'label', tr("Select a common service level for this system's subscriptions:"))
    except TimeoutError:
        return (False, "Cannot find SLA label - not in SLA panel.")
    default_handler(element, app_node, sla_panel)

@handle_act('/sla')
def sla_handler(element, app_node, local_node):
    sla_label = getnode(local_node, 'label', tr("Select a common service level for this system's subscriptions:"))
    sla_combo = getnode(sla_label.parent, 'combo box')
    required_sla = get_attr(element, 'value')
    sla_combo.click()
    combo_item = getnode(sla_combo, 'menu item', required_sla)
    combo_item.click()

@handle_chck('/sla')
def sla_chck(element, app_node, local_node):
    required_sla = get_attr(element, 'value')
    sla_label = getnode(local_node, 'label', tr("Select a common service level for this system's subscriptions:"))
    sla_combo = getnode(sla_label.parent, 'combo box')
    if sla_combo.combovalue == required_sla:
        return True
    return (False, "Selected SLA: '%s' Expected: '%s' sla_combo properties = %s  value=%s, combovalue=%s" %(sla_combo.text, required_sla, dir(sla_combo), sla_combo.value, sla_combo.combovalue))

@handle_act('/back')
def back_handler(element, app_node, local_node):
    back_button = getnode(local_node.parent.parent, "push button", tr("Back"))
    back_button.click()

@handle_act('/next')
def next_button_handler(element, app_node, local_node):
    next_button = getnode(local_node.parent.parent, "push button", tr("Next"))
    next_button.click()

@handle_chck('/next')
def next_button_check(element, app_node, local_node):
    # we shouldn't be on SLA panel
    try:
        sla_label = getnode(local_node, 'label', tr("Select a common service level for this system's subscriptions:"))
        return (False, "SLA panel is still showing")
    except TimeoutError:
        return True

