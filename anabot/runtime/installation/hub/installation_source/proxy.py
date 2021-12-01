# -*- coding: utf-8 -*-

from anabot.conditions import is_distro_version
from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, get_attr_bool, getnode, getnode_scroll, getnodes, getparent, getsibling
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError, NonexistentError
from anabot.runtime.installation.common import done_handler
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.asserts import assertPasswordTextInputEquals as aptie
from anabot.runtime.asserts import assertTextInputEquals as atie
from anabot.runtime.asserts import assertCheckboxEquals as ace
from .common import PASS, source_context, check_infobar_message

_local_path = '/installation/hub/installation_source/proxy'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)
proxy_context = "GUI|Software Source|Proxy Dialog"


def proxy_manipulate(element, app_node, local_node, dry_run):  
    try:
        proxy_button = getnode(local_node, "push button", tr("_Proxy setup...", context="GUI|Software Source"))
        if dry_run:
            return PASS
    except TimeoutError:
        return NotFound("proxy setup button")
    proxy_button.click()

    try:
        proxy_dialog = getparent(getnode(app_node, "check box", tr("_Enable HTTP Proxy", context=proxy_context)), "dialog")
    except TimeoutError:
        return NotFound("proxy settings dialog or 'Enable HTTP Proxy' checkbox")
    default_handler(element, app_node, proxy_dialog)
    return PASS

@handle_act('')
def proxy_handler(element, app_node, local_node):
    return proxy_manipulate(element, app_node, local_node, False)

@handle_chck('')
def proxy_check(element, app_node, local_node):
    return proxy_manipulate(element, app_node, local_node, True)


def proxy_status_manipulate(element, app_node, local_node, dry_run):
    enable = get_attr_bool(element, "enable", True)
    try:
        checkbox = getnode(local_node, "check box", tr("_Enable HTTP Proxy", context=proxy_context))
    except TimeoutError:
        return NotFound("sensitive (active) Enable HTTP Proxy checkbox", where="proxy dialog")
    if dry_run:
        return ace(checkbox, enable, "Enable HTTP Proxy")
    else:
        checkbox.click()
    return PASS

@handle_act('/status')
def proxy_status_handler(element, app_node, local_node):
    return proxy_status_manipulate(element, app_node, local_node, False)

@handle_chck('/status')
def proxy_status_check(element, app_node, local_node):
    return proxy_status_manipulate(element, app_node, local_node, True)


def proxy_host_manipulate(element, app_node, local_node, dry_run):
    host = get_attr(element, "value")
    try:
        host_field = getnodes(local_node, "text")[0]
    except TimeoutError:
        return NotFound("sensitive (active) proxy host field", where="Proxy dialog")
    if dry_run:
        return atie(host_field, host, "proxy host field")
    else:
        host_field.delete_text(0, -1)
        host_field.typeText(host)
        return PASS

@handle_act('/host')
def proxy_host_handler(element, app_node, local_node):
    return proxy_host_manipulate(element, app_node, local_node, False)

@handle_chck('/host')
def proxy_host_check(element, app_node, local_node):
    return proxy_host_manipulate(element, app_node, local_node, True)


def proxy_authentication_manipulate(element, app_node, local_node, dry_run):
    enable_auth = get_attr_bool(element, "enable", True)
    try:
        checkbox = getnode(local_node, "check box", tr("_Use Authentication", context=proxy_context))
    except TimeoutError:
        return NotFound("sensitive (active) Enable HTTP Proxy checkbox", where="proxy dialog")
    if dry_run:
        return ace(checkbox, enable_auth, "Use Authentication")
    else:
        checkbox.click()
    return PASS

@handle_act('/authentication')
def proxy_authentication_handler(element, app_node, local_node):
    return proxy_authentication_manipulate(element, app_node, local_node, False)

@handle_chck('/authentication')
def proxy_authentication_check(element, app_node, local_node):
    return proxy_authentication_manipulate(element, app_node, local_node, True)

def proxy_username_manipulate(element, app_node, local_node, dry_run):
    username = get_attr(element, "value")
    try:
        username_field = getnodes(local_node, "text")[1]
    except (TimeoutError, IndexError):
        return NotFound("sensitive (active) proxy username field", where="Proxy dialog")
    if dry_run:
        return atie(username_field, username, "proxy username field")
    else:
        username_field.delete_text(0, -1)
        username_field.typeText(username)
        return PASS

@handle_act('/username')
def proxy_username_handler(element, app_node, local_node):
    return proxy_username_manipulate(element, app_node, local_node, False)

@handle_chck('/username')
def proxy_username_check(element, app_node, local_node):
    return proxy_username_manipulate(element, app_node, local_node, True)

def proxy_password_manipulate(element, app_node, local_node, dry_run):
    password = get_attr(element, "value")
    try:
        password_field = getnode(local_node, "password text")
    except TimeoutError:
        return NotFound("sensitive (active) proxy password field", where="Proxy dialog")
    if dry_run:
        return aptie(password_field, password, "proxy password field")
    else:
        password_field.delete_text(0, -1)
        password_field.typeText(password)
        return PASS

@handle_act('/password')
def proxy_password_handler(element, app_node, local_node):
    return proxy_password_manipulate(element, app_node, local_node, False)

@handle_chck('/password')
def proxy_password_check(element, app_node, local_node):
    return proxy_password_manipulate(element, app_node, local_node, True)


def proxy_cancel_manipulate(element, app_node, local_node, dry_run):
    try:
        cancel_button = getnode(local_node, "push button", tr("_Cancel", context=proxy_context))
    except TimeoutError:
        return NotFound("Cancel button", where="proxy dialog")
    # proxy dialog doesn't exist after clicking on OK or Cancel
    except NonexistentError as e:
        if dry_run:
            return PASS
        else:
            return Fail(e)
    cancel_button.click()
    return PASS

@handle_act('/cancel')
def proxy_cancel_handler(element, app_node, local_node):
    return proxy_cancel_manipulate(element, app_node, local_node, False)

@handle_chck('/cancel')
def proxy_cancel_check(element, app_node, local_node):
    return proxy_cancel_manipulate(element, app_node, local_node, True)

def proxy_ok_manipulate(element, app_node, local_node, dry_run):
    try:
        ok_button = getnode(local_node, "push button", tr("_OK", context=proxy_context))
    except TimeoutError:
        return NotFound("OK button", where="proxy dialog")
    # proxy dialog doesn't exist after clicking on OK or Cancel
    except NonexistentError as e:
        if dry_run:
            return PASS
        else:
            return Fail(e)
    if dry_run:
        if local_node.visible:
            return Fail("Proxy dialog (filler) is still visible.")
        else:
            return PASS
    ok_button.click()
    return PASS

@handle_act('/ok')
def proxy_ok_handler(element, app_node, local_node):
    return proxy_ok_manipulate(element, app_node, local_node, False)

@handle_chck('/ok')
def proxy_ok_check(element, app_node, local_node):
    return proxy_ok_manipulate(element, app_node, local_node, True)
