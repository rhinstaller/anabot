from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode, getnodes, get_attr, getsibling
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound

from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check

_local_path = '/installation/hub/connect_to_redhat/subscription'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

PASS = Pass()

@handle_act('')
def base_handler(element, app_node, local_node):
    # don't do anything, just pass
    return PASS

@handle_chck('')
def base_check(element, app_node, local_node):
    # proper checks go here
    pass
