import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode
from anabot.runtime.translate import tr



_local_path = '/initial_setup/hub/subscription_manager'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def base_handler(element, app_node, local_node):
    sm_selector = getnode(app_node, "spoke selector", tr("Register system"))
    sm_selector.click()
    sm_panel = getnode(app_node,'panel', tr('ToDo'))
    default_handler(element, app_node, sm_panel)

@handle_act('/server_panel')
def server_panel_handler(element, app_node, local_node):
    panel = local_node
    default_handler(element, app_node, panel)

@handle_act('/server_panel/server')
def server_panel_handler(element, app_node, local_node):
    server = get_attr(element, 'value')
    # ToDo fill text field

@handle_act('/server_panel/proxy')
def proxy_dialog_handler(element, app_node, local_node):
    # ToDo find Configure Proxy button and click it
    # ToDo find proxy dialog
    proxy_dialog = None
    default_handler(element, app_node, proxy_dialog)

@handle_act('/server_panel/proxy/proxy_server')
def proxy_dialog_proxy_handler(element, app_node, local_node):
    proxy_text = get_attr(element, 'value')
    if proxy_text != "":
        # ToDo tick I would like to connect via an HTTP proxy. checkbox
        # ToDo find and fill text for proxy server
        pass

@handle_act('/server_panel/proxy/OK')
def proxy_dialog_ok_handler(element, app_node, local_node):
    ok_button = getnode(local_node, "push button", tr("_Save", False))
    ok_button.click()

@handle_act('/server_panel/next')
def server_panel_next_handler(element, app_node, local_node):
    next_button = getnode(local_node, "push button", tr("_Next", False))
    next_button.click()

@handle_act('/user_panel')
def user_panel_handler(element, app_node, local_node):
    user_panel = None
    # ToDo find proper panel
    default_handler(element, app_node, user_panel)

@handle_act('/user_panel/username')
def user_panel_handler(element, app_node, local_node):
    username = get_attr(element, 'value')
    # ToDo find proper text field and fill it

@handle_act('/user_panel/password')
def user_panel_handler(element, app_node, local_node):
    user_panel = None
    # ToDo find proper panel
    default_handler(element, app_node, user_panel)

@handle_act('/user_panel/next')
def user_panel_next(element, app_node, local_node):
    next_button = getnode(local_node, "push button", tr("Register", False))
    next_button.click()

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()



