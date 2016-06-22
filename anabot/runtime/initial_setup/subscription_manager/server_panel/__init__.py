import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getparents
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError

_local_path = '/initial_setup/subscription_manager/server_panel'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

# import proxy dialog submodule
from . import proxy

@handle_act('')
def server_panel_handler(element, app_node, local_node):
    panel = local_node
    default_handler(element, app_node, panel)
    return (True,None)

@handle_chck('')
def server_panel_chck(element, app_node, local_node):
    # no idea how to check this part
    return action_result(element)

@handle_act('/server')
def server_input_handler(element, app_node, local_node):
    server_text = get_attr(element, 'value')
    server_input = getnode(local_node, 'text', 'server_entry')
    server_input.actions['activate'].do()
    server_input.typeText(server_text)

@handle_chck("/server")
def server_input_chck(element, app_node, local_node):
    server_text = get_attr(element, 'value')
    server_input = getnode(local_node, 'text', 'server_entry')
    if server_input.text == server_text:
        return (True, "Server name is expected one")
    else:
        return (False, "Server name is not requested one '%s' vs expected '%s'", (server_input.text, server_text,))

@handle_act('/default_server')
def server_default_button_handler(element, app_node, local_node):
    default_btn = getnode(local_node, 'push button', 'default_button')
    default_btn.click()

@handle_chck('/default_server')
def server_default_button_chck(element, app_node, local_node):
    server_input = getnode(local_node.parent, 'text', 'server_entry')
    server_text = "subscription.rhn.redhat.com"
    if server_input.text == server_text:
        return (True, "Server name is expected one")
    else:
        return (False, "Server name is not requested one '%s' vs expected '%s'", (server_input.text, server_text,))

@handle_act('/back')
def back_handler(element, app_node, local_node):
    back_button = getnode(local_node.parent.parent, "push button", tr("Back"))
    back_button.click()

@handle_chck('/back')
def back_check(element, app_node, local_node):
    # We shouldn't be on server panel, should we?
    sm_panels = getnode(app_node, 'page tab list', 'register_notebook')
    try:
        server_input = getnode(sm_panels, 'text', 'server_entry', visible=False)
    except TimeoutError:
        return (False, "Server panel is still showing")
    return True
    
@handle_act('/next')
def server_panel_next_handler(element, app_node, local_node):
    next_button = getnode(local_node.parent.parent, "push button", tr("Next"))
    next_button.click()

@handle_chck('/next')
def server_panel_next_chck(element, app_node, local_node):
    # We shouldn't be on server panel, should we?
    sm_panels = getnode(app_node, 'page tab list', 'register_notebook')
    try:
        server_input = getnode(sm_panels, 'text', 'server_entry', visible=False)
    except TimeoutError:
        return (False, "Server panel is still showing")
    return True
    
