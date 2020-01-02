from anabot.runtime.decorators import check_action_result
from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode, getnodes, get_attr, getsibling
from anabot.runtime.functions import handle_checkbox, check_checkbox
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound

from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check

_local_path = '/installation/hub/connect_to_redhat/options'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

PASS = Pass()

def options_button(local_node):
    # DIRTY HACK
    # just looking for only one "toogle button" which should be hopefully "Options"
    return getnode(local_node, "toggle button")

def options_visible(local_node):
    try:
        getnodes(local_node)
        return True
    except TimeoutError:
        return False

@handle_act('')
def base_handler(element, app_node, local_node):
    visible = get_attr(element, 'visible')
    options = options_button(local_node)
    if visible is not None and options_visible(options) != (visible == "yes"):
        # Options (toggle button) is not clickable by dogtail
        options.actions['activate'].do()
    return default_handler(element, app_node, options)

@handle_chck('')
def base_check(element, app_node, local_node):
    visible = get_attr(element, 'visible')
    options = options_button(local_node)
    if visible is not None:
        visible_state = options_visible(options)
        expectation = visible == "yes"
        if visible_state != expectation:
            return Fail("Options visibility (visible: %s) doesn't match expectations (visible: %s)" % (visible_state, expectation))
    return PASS

@handle_act('/http_proxy')
def http_proxy_handler(element, app_node, local_node):
    enabled = get_attr(element, 'used', None)
    checkbox = getnode(local_node, "check box", tr("Use HTTP proxy"))
    if enabled is not None and enabled != checkbox.checked:
        checkbox.click()
    panel = getsibling(checkbox, -1, "panel", visible=None, sensitive=None)
    return default_handler(element, app_node, panel)

@handle_chck('/http_proxy')
def http_proxy_check(element, app_node, local_node):
    enabled = get_attr(element, 'used', None)
    if enabled is not None:
        enabled = enabled == "yes"
        result, msg = check_checkbox(local_node, enabled == "yes", tr("Use HTTP proxy"))
        if not result:
            return result, msg
        checkbox = getnode(local_node, "check box", tr("Use HTTP proxy"))
        panel = getsibling(checkbox, -1, "panel", visible=None, sensitive=None)
        if panel.visible != (enabled == "yes") or panel.sensitive != (enabled == "yes"):
            return Fail("Requested Use HTTP proxy status (%s) doesn't match widgets visibility (%s) or sensitivity (%s)." % (enabled, panel.visible, panel.sensitive))
    return PASS

@handle_act('/http_proxy/location')
def http_proxy_location_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    location = getnodes(local_node, "text")[1]
    location.typeText(value)

@handle_chck('/http_proxy/location')
def http_proxy_location_check(element, app_node, local_node):
    value = get_attr(element, "value")
    location = getnodes(local_node, "text")[1]
    return location.text == value

@handle_act('/http_proxy/username')
def http_proxy_username_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    username = getnodes(local_node, "text")[0]
    username.typeText(value)

@handle_chck('/http_proxy/username')
def http_proxy_username_check(element, app_node, local_node):
    value = get_attr(element, "value")
    username = getnodes(local_node, "text")[0]
    return username.text == value

@handle_act('/http_proxy/password')
def http_proxy_password_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password = getnode(local_node, "password text")
    password.typeText(value)

@handle_chck('/http_proxy/password')
def http_proxy_password_check(element, app_node, local_node):
    value = get_attr(element, "value")
    password = getnode(local_node, "password text")
    return password.text == value

@handle_act('/use_custom_server_url')
def use_custom_server_url_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr("Custom server URL"))
    return handle_checkbox(checkbox, element)

@handle_chck('/use_custom_server_url')
def use_custom_server_url_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr("Custom server URL"))
    return check_checkbox(checkbox, element, 'Custom server URL')

@handle_act('/custom_server_url')
def custom_server_url_handler(element, app_node, local_node):
    value = get_attr(element, 'value')
    # UGLY HACK
    checkbox = getnode(local_node, "check box", tr("Custom server URL"))
    panel = getsibling(checkbox, 1, 'panel', visible=None, sensitive=None)
    input_text = getnode(panel, 'text')
    input_text.typeText(value)
    return PASS

@handle_chck('/custom_server_url')
def custom_server_url_check(element, app_node, local_node):
    value = get_attr(element, 'value')
    # UGLY HACK
    checkbox = getnode(local_node, "check box", tr("Custom server URL"))
    panel = getsibling(checkbox, 1, 'panel', visible=None, sensitive=None)
    input_text = getnode(panel, 'text')
    if input_text.text != value:
        return Fail("Present text '%s' doesn't match expectation: '%s'" % (input_text.text, value))
    return PASS

@handle_act('/use_custom_base_url')
def use_custom_base_url_handler(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr("Custom base URL"))
    return handle_checkbox(checkbox, element)

@handle_chck('/use_custom_base_url')
def use_custom_base_url_check(element, app_node, local_node):
    checkbox = getnode(local_node, "check box", tr("Custom base URL"))
    return check_checkbox(checkbox, element, 'Custom base URL')

@handle_act('/custom_base_url')
def custom_base_url_handler(element, app_node, local_node):
    value = get_attr(element, 'value')
    # UGLY HACK
    checkbox = getnode(local_node, "check box", tr("Custom base URL"))
    panel = getsibling(checkbox, -1, 'panel', visible=None, sensitive=None)
    input_text = getnode(panel, 'text')
    input_text.typeText(value)
    return PASS

@handle_chck('/custom_base_url')
def custom_base_url_check(element, app_node, local_node):
    value = get_attr(element, 'value')
    # UGLY HACK
    checkbox = getnode(local_node, "check box", tr("Custom base URL"))
    panel = getsibling(checkbox, -1, 'panel', visible=None, sensitive=None)
    input_text = getnode(panel, 'text')
    input_text = getnode(panel, 'text')
    if input_text.text != value:
        return Fail("Present text '%s' doesn't match expectation: '%s'" % (input_text.text, value))
    return PASS
