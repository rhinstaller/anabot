import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getparents
from anabot.runtime.translate import tr
from time import sleep


_local_path = '/initial_setup/subscription_manager'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

# import submodules
from . import server_panel, account_panel, sla_panel, subscription_panel

@handle_act('')
def base_handler(element, app_node, local_node):
    sm_selector = getnode(app_node, "spoke selector", tr("Subscription Manager"))
    sm_selector.click()
    sm_panels = getnode(app_node, 'page tab list', 'register_notebook')
    default_handler(element, app_node, sm_panels)
    return (True, None)

@handle_chck('')
def base_check(element, app_node, local_node):
    # no check
    return action_result(element)

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(getparents(local_node, node_type='filler')[4], "push button", tr("_Done", False))
    done_button.click()

@handle_chck('/done')
def done_check(element, app_node, local_node):
    sm_selector = getnode(app_node, "spoke selector", tr("Subscription Manager"))
    if (sm_selector != None):
        return (True, "We are back in hub")
    return (False, "Cannot find Subscription Manager spoke selector")

