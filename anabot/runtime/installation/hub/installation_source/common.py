# -*- coding: utf-8 -*-

from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getnodes
from fnmatch import fnmatchcase
from anabot.runtime.asserts import assertPasswordTextInputEquals as aptie
from anabot.runtime.asserts import assertTextInputEquals as atie
from anabot.runtime.asserts import assertComboBoxEquals as acbe
import re

source_context = "GUI|Software Source"
PASS = Pass()

_local_path = '/installation/hub/installation_source'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

def repo_url(url_field, repo_url, dry_run):
    if dry_run:
        return atie(url_field, repo_url, "repo URL")
    else:
        url_field.delete_text(0, -1)
        url_field.typeText(repo_url)
    return PASS

def repo_url_type(app_node, url_type_combo, url_type, dry_run):
    url_type_map = {
        "repo":         "repository URL",
        "mirrorlist":   "mirrorlist",
        "metalink":     "metalink",
    }

    try:
        url_type = tr(url_type_map[url_type])
    except KeyError:
        return Fail("Unknown URL type: %s" % url_type)
    
    if not url_type_combo.sensitive:
            return Fail("URL type combo box is not sensitive (active), probably because of the selected protocol.")

    if dry_run:
        return acbe(url_type_combo, url_type, "URL type")
    else:
        url_type_combo.click()
        try:
            combo_window = getnode(app_node, "window")
            menuitem = getnode(combo_window, "menu item", url_type)
        except TimeoutError:
            return NotFound("URL type item '%s'" % url_type, where="combo box")
        menuitem.click()
    return PASS

def repo_url_protocol(app_node, url_protocol_combo, url_protocol, dry_run):
    if dry_run:
        return acbe(url_protocol_combo, url_protocol, "URL protocol")
    else:
        url_protocol_combo.click()
        try:
            combo_window = getnode(app_node, "window")
            menuitem = getnode(combo_window, "menu item", url_protocol)
        except TimeoutError:
            return NotFound("URL prefix item '%s'" % url_protocol, where="combo box")
        menuitem.click()
    return PASS

def check_infobar_message(app_node, expected_message=None, repo_name=None):
    if expected_message is not None:
        translated_message = tr(expected_message)
    else:
        translated_message = "*"
    if repo_name is not None and "%s" in expected_message:
        translated_message = translated_message % repo_name
    elif expected_message is not None:
        translated_message = translated_message.replace("%s", "*")

    try:
        infobar = getnode(app_node, "info bar")
        infobar_message = getnode(infobar, "label").name
    except TimeoutError:
        return NotFound("Info bar or info bar message")

    if fnmatchcase(infobar_message, translated_message):
        return PASS
    else:
        return Fail("Message in info bar '%s' doesn't match the expected message '%s'." %
            (infobar_message, translated_message))

@handle_act('/infobar')
@handle_act('/additional_repo/infobar')
@handle_act('/additional_repo/select/infobar')
def infobar_handler(element, app_node, local_node):
    # no action makes sense here, only a check
    return PASS

@handle_chck('/infobar')
@handle_chck('/additional_repo/infobar')
@handle_chck('/additional_repo/select/infobar')
def infobar_check(element, app_node, local_node):
    message = get_attr(element, "message")
    repo_name = get_attr(element, "repo_name")
    return check_infobar_message(app_node, message, repo_name)
