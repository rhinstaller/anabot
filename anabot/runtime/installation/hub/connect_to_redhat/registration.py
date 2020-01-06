from anabot.runtime.decorators import check_action_result
from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode, getnodes, get_attr, getparent, getsibling
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound

from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check

from . import subscriptions

_local_path = '/installation/hub/connect_to_redhat/registration'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

PASS = Pass()

@handle_act('')
def base_handler(element, app_node, local_node):
    # don't do anything, only process sub elements
    unregister_button = getnode(local_node, "push button", tr("_Unregister", context="GUI|subscription|Unregister"))
    local_node = getparent(unregister_button, "page tab")
    return default_handler(element, app_node, local_node)

@handle_chck('')
def base_check(element, app_node, local_node):
    # proper checks go here
    pass

handle_act('/method', default_handler)
@handle_chck('/method')
def method_check(element, app_node, local_node):
    pass

handle_act('/system_purpose', default_handler)
@handle_chck('/system_purpose')
def system_purpose_check(element, app_node, local_node):
    pass

handle_act('/system_purpose/role', default_handler)
@handle_chck('/system_purpose/role')
def system_purpose_role_check(element, app_node, local_node):
    pass

handle_act('/system_purpose/sla', default_handler)
@handle_chck('/system_purpose/sla')
def system_purpose_sla_check(element, app_node, local_node):
    pass

handle_act('/system_purpose/usage', default_handler)
@handle_chck('/system_purpose/usage')
def system_purpose_usage_check(element, app_node, local_node):
    pass

handle_act('/insights', default_handler)
@handle_chck('/insights')
def insights_check(element, app_node, local_node):
    pass
