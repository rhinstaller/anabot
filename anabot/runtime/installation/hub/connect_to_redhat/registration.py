from anabot.runtime.decorators import check_action_result
from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode, getnodes, get_attr, getparent, getsibling
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.asserts import assertLabelEquals as ale

from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check

from . import subscriptions

_local_path = '/installation/hub/connect_to_redhat/registration'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

PASS = Pass()

def unregister_button(local_node):
    return getnode(local_node, "push button", tr("_Unregister", context="GUI|subscription|Unregister"))

@handle_act('')
def base_handler(element, app_node, local_node):
    # don't do anything, only process sub elements
    unreg_button = unregister_button(local_node)
    local_node = getparent(unreg_button, "page tab")
    return default_handler(element, app_node, local_node)

@handle_chck('')
@check_action_result
def base_check(element, app_node, local_node):
    return PASS

def registration_info_panel(local_node):
    unreg_button = unregister_button(local_node)
    sibling_filler = getparent(unreg_button, 'filler')
    return getsibling(sibling_filler, 1, "panel")

handle_act('/account_organization', default_handler)
@handle_chck('/account_organization')
def organization_check(element, app_node, local_node):
    org = get_attr(element, "value")
    return ale(getnode(local_node, "label", "Organization:.*"), ("Organization: %s" % org), "Organization")

handle_act('/method', default_handler)
@handle_chck('/method')
def method_check(element, app_node, local_node):
    account = get_attr(element, "account")
    organization = get_attr(element, "organization")
    panel = registration_info_panel(local_node)
    # DIRTY HACK
    label = getnodes(panel, "label")[5]
    if account is not None:
        return ale(label, ("Registered with account %s" % account), "Account information")
    if organization is not None:
        return ale(label, ("Registered with organization %s" % organization), "Organization information")
    return Fail("No method was checked!")

@handle_act('/system_purpose')
def system_purpose_handler(element, app_node, local_node):
    panel = registration_info_panel(local_node)
    return default_handler(element, app_node, panel)

@handle_chck('/system_purpose')
def system_purpose_check(element, app_node, local_node):
    return PASS

handle_act('/system_purpose/role', default_handler)
@handle_chck('/system_purpose/role')
def system_purpose_role_check(element, app_node, local_node):
    role = get_attr(element, "value")
    return ale(getnode(local_node, "label", "Role:.*"), ("Role: %s" % role), "System purpose role")

handle_act('/system_purpose/sla', default_handler)
@handle_chck('/system_purpose/sla')
def system_purpose_sla_check(element, app_node, local_node):
    sla = get_attr(element, "value")
    return ale(getnode(local_node, "label", "SLA:.*"), ("SLA: %s" % sla), "System purpose SLA")

handle_act('/system_purpose/usage', default_handler)
@handle_chck('/system_purpose/usage')
def system_purpose_usage_check(element, app_node, local_node):
    usage = get_attr(element, "value")
    return ale(getnode(local_node, "label", "Usage:.*"), ("Usage: %s" % usage), "System purpose usage")

handle_act('/insights', default_handler)
@handle_chck('/insights')
def insights_check(element, app_node, local_node):
    used = get_attr(element, "used", "yes") == "yes"
    if used:
        expected_text = tr("Connected to Red Hat Insights")
    else:
        expected_text = tr("Not connected to Red Hat Insights")
    panel = registration_info_panel(local_node)
    label = getnodes(panel, "label")[1]
    return ale(label, expected_text, "Insights enabled")
