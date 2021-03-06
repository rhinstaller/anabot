import logging
logger = logging.getLogger('anabot')


from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getparents, press_key
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from time import sleep
import re

_local_path = '/initial_setup/subscription_manager/server_panel/proxy'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def proxy_dialog_handler(element, app_node, local_node):
    proxy_btn = getnode(local_node, "push button", 'proxy_button')
    proxy_btn.click()
    proxy_dialog = getnode(app_node, 'dialog', tr('Proxy Configuration'))
    default_handler(element, app_node, proxy_dialog)
    return True

@handle_act('/use_proxy')
def use_proxy_handler(element, app_node, local_node):
    check_it = get_attr(element, 'checked')
    check_it = (check_it == 'yes')
    proxy_checkbox = getnode(local_node, "check box", 'Proxy Checkbox')
    if (proxy_checkbox.checked != check_it):
        proxy_checkbox.click()

@handle_chck('/use_proxy')
def use_proxy_chck(element, app_node, local_node):
    check_it = get_attr(element, 'checked')
    check_it = (check_it == 'yes')
    proxy_checkbox = getnode(local_node, "check box", 'Proxy Checkbox')
    return proxy_checkbox.checked == check_it

@handle_act('/proxy_server')
def server_handler(element, app_node, local_node):
    proxy_text = get_attr(element, 'value')
    proxy_input = getnode(local_node, 'text', "Proxy Location Text")
    proxy_input.typeText(proxy_text)
    # now activate some other element (press <Tab>)
    # - software automagically appends default ':3128' port
    press_key('\t')

@handle_chck('/proxy_server')
def server_chck(element, app_node, local_node):
    proxy_text = get_attr(element, 'value')
    contains_port = re.match(r'.*:[0-9]+$', proxy_text) # match() starts at begining of string
    if not contains_port:
        # append default port
        proxy_text = proxy_text + ':3128'
    proxy_input = getnode(local_node, 'text', "Proxy Location Text")
    if proxy_input.text != proxy_text:
        return (False, "Proxy server hostname is '%s' expected is '%s'" % (proxy_input.text, proxy_text))
    return True

@handle_act('/cancel')
def cancel_handler(element, app_node, local_node):
    cancel_button = getnode(local_node, "push button", "Cancel Button")
    cancel_button.click()

@handle_act('/save')
def save_handler(element, app_node, local_node):
    ok_button = getnode(local_node, "push button", "Save Button")
    ok_button.click()
    return True

@handle_act('/test_connection')
def test_connection_handler(element, app_node, local_node):
    test_button = getnode(local_node, "push button", "Test Connection Button")
    test_button.click()
    sleep(2)
    # wait until progress_frame disappears
    try:
        while True:
            progress_frame = getnode(app_node, 'frame', tr('Testing Connection'))
    except TimeoutError:
        pass

@handle_chck('/test_connection')
def test_connection_chck(element, app_node, local_node):
    result_label = getnode(local_node, "label", 'connectionStatusLabel')
    if result_label.text == tr('Proxy connection succeeded'):
        return True
    return (False, "Connection test message was:'%s'  expected:'%s'" % (result_label.text, tr('Proxy connection succeeded')))
