# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from fnmatch import fnmatchcase

from anabot.conditions import is_distro_version
from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, get_attr_bool, getnode, getnode_scroll, getnodes, getparent, getsibling, disappeared, combo_scroll
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from anabot.runtime.installation.common import done_handler
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.asserts import assertPasswordTextInputEquals as aptie
from anabot.runtime.asserts import assertTextInputEquals as atie
from .common import PASS, source_context, check_infobar_message, repo_url, repo_url_type, repo_url_protocol

import re

_local_path = '/installation/hub/installation_source/additional_repo'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)
initial_repos = {}
_repolist_without_removed_repo = []

def get_repolist(local_node, return_nodes=False, check=lambda x: True):
    try:
        repo_table = getnode(local_node, "table")
    except TimeoutError:
        return NotFound("repo or table cells")
    try:
        cell_nodes = getnodes(repo_table, "table cell")
    except TimeoutError:
        filtered_nodes = []
    else:
        filtered_nodes = [n for n in cell_nodes[1::2] if check(n)]

    if return_nodes:
        return filtered_nodes
    else:
        return {n.name: getsibling(n, -1).checked for n in filtered_nodes}

@handle_act('')
def additional_repo_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    return PASS

@handle_chck('')
def additional_repo_check(element, app_node, local_node):
    return PASS

@handle_act('/select')
def select_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    enabled = get_attr(element, "enabled")

    def check(cell):
        matches = True
        if name is not None:
            matches = fnmatchcase(cell.name, name)
        if matches and enabled is not None:
            matches = getsibling(cell, -1).checked == enabled
        return matches

    for repo in get_repolist(local_node, return_nodes=True, check=check):
        repo.click()
        default_handler(element, app_node, local_node)

    return PASS

@handle_chck('/select')
def select_check(element, app_node, local_node):
    logger.debug("Check for select is using just result of the action itself")
    return action_result(element)

@handle_act('/select/remove')
def remove_handler(element, app_node, local_node):
    repolist_nodes = get_repolist(local_node, True)
    global _repolist_without_removed_repo
    _repolist_without_removed_repo = [i.name for i in repolist_nodes if not i.selected]

    try:
        toolbox = getnode(local_node, "tool bar")
    except TimeoutError:
        return NotFound("tool bar")
    try:
        remove_btn = getnode(toolbox, "push button", tr("_Remove", context="GUI|Software Source"))
    except TimeoutError:
        return NotFound("remove repo button")
    remove_btn.click()
    return PASS

@handle_chck('/select/remove')
def remove_check(element, app_node, local_node):
    current_repolist = [i.name for i in get_repolist(local_node, True)]

    if current_repolist == _repolist_without_removed_repo:
        return PASS
    else:
        return Fail("The required additional repo has not been removed from repo list.")

def additional_repo_name(local_node, repo_name, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        name_field = getnodes(getparent(name_label), "text", sensitive=None)[0]
    except TimeoutError:
        return NotFound("additional repo name field or label")
    if dry_run:
        if re.match(repo_name, name_field.text) is None:
            return Fail("repo name '%s' doesn't match the expected name '%s'" % 
                (name_field.text, repo_name))
    else:
        name_field.delete_text(0, -1)
        name_field.typeText(repo_name)
    return PASS

def additional_repo_url(local_node, url, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        url_field = getnodes(getparent(name_label), "text", sensitive=None)[3]
    except TimeoutError:
        return NotFound("additional repo name label or url field")
    return repo_url(url_field, url, dry_run)

def additional_repo_url_protocol(app_node, local_node, url_protocol, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        url_protocol_combo = getnodes(getparent(name_label), "combo box", sensitive=None)[1]
    except (TimeoutError, IndexError):
        return NotFound("additional repo name label or url prefix combo box")
    return repo_url_protocol(app_node, url_protocol_combo, url_protocol, dry_run)

def additional_repo_url_type(app_node, local_node, url_type, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        url_type_combo = getnodes(getparent(name_label), "combo box", sensitive=None)[0]
    except TimeoutError:
        return NotFound("additional repo name label or url type combo box")
    return repo_url_type(app_node, url_type_combo, url_type, dry_run)

def additional_repo_proxy_url(local_node, proxy_url, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        proxy_url_field = getnodes(getparent(name_label), "text")[2]
    except TimeoutError:
        return NotFound("additional repo name label or proxy url field")
    if dry_run:
        return atie(proxy_url_field, proxy_url, "additional repo proxy URL")
    else:
        proxy_url_field.delete_text(0, -1)
        proxy_url_field.typeText(proxy_url)
    return PASS

def additional_repo_proxy_username(local_node, proxy_username, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        proxy_username_field = getnodes(getparent(name_label), "text")[1]
    except TimeoutError:
        return NotFound("additional repo name label or proxy username field")
    if dry_run:
        return atie(proxy_username_field, proxy_username, "proxy username")
    else:
        proxy_username_field.delete_text(0, -1)
        proxy_username_field.typeText(proxy_username)
    return PASS

def additional_repo_proxy_password(local_node, proxy_password, dry_run):
    try:
        name_label = getnode(local_node, "label", tr("_Name:", context=source_context))
        proxy_password_field = getnode(getparent(name_label), "password text")
    except TimeoutError:
        return NotFound("additional repo name label or proxy url field")
    if dry_run:
        return aptie(proxy_password_field, proxy_password, "proxy")
    else:
        proxy_password_field.delete_text(0, -1)
        proxy_password_field.typeText(proxy_password)
    return PASS

@handle_act('/select/name')
def addrepo_name_handler(element, app_node, local_node):
    repo_name = get_attr(element, "value")
    return additional_repo_name(local_node, repo_name, False)

@handle_chck('/select/name')
def addrepo_name_check(element, app_node, local_node):
    repo_name = get_attr(element, "value", r"New_Repository(_\d+)?")
    return additional_repo_name(local_node, repo_name, True)

def addrepo_status(local_node, enabled, dry_run):
    try:
        repo_table = getnode(local_node, "table")
        checkbox_cell = [c for c in getnodes(repo_table, "table cell") if c.selected][0]
    except TimeoutError:
        return NotFound("epo table or repo status checkbox")
    if dry_run:
        if checkbox_cell.checked == enabled:
            return PASS
        else:
            return Fail("Repo status is not in accordance with expected status (enabled/disabled).")
    else:
        if checkbox_cell.checked != enabled:
            checkbox_cell.click()
    return PASS

def addrepo_status_manipulate(element, app_node, local_node, dry_run):
    enabled = get_attr_bool(element, "enabled")
    return addrepo_status(local_node, enabled, dry_run)

@handle_act('/select/status')
def addrepo_status_handler(element, app_node, local_node):
    return addrepo_status_manipulate(element, app_node, local_node, False)

@handle_chck('/select/status')
def addrepo_status_check(element, app_node, local_node):
    return addrepo_status_manipulate(element, app_node, local_node, True)

@handle_act('/select/url')
def addrepo_url_handler(element, app_node, local_node):
    repo_url = get_attr(element, "value")
    return additional_repo_url(local_node, repo_url, False)

@handle_chck('/select/url')
def addrepo_url_check(element, app_node, local_node):
    repo_url = get_attr(element, "value")
    return additional_repo_url(local_node, repo_url, True)

@handle_act('/select/url_protocol')
def addrepo_url_protocol_handler(element, app_node, local_node):
    url_protocol = get_attr(element, "value")
    return additional_repo_url_protocol(app_node, local_node, url_protocol, False)

@handle_chck('/select/url_protocol')
def addrepo_url_protocol_check(element, app_node, local_node):
    url_protocol = get_attr(element, "value")
    return additional_repo_url_protocol(app_node, local_node, url_protocol, True)

@handle_act('/select/url_type')
def addrepo_url_type_handler(element, app_node, local_node):
    url_type = get_attr(element, "value")
    return additional_repo_url_type(app_node, local_node, url_type, False)

@handle_chck('/select/url_type')
def addrepo_url_type_check(element, app_node, local_node):
    url_type = get_attr(element, "value")
    return additional_repo_url_type(app_node, local_node, url_type, True)

@handle_act('/select/proxy_url')
def addrepo_proxy_url_handler(element, app_node, local_node):
    proxy_url = get_attr(element, "value")
    return additional_repo_proxy_url(local_node, proxy_url, False)

@handle_chck('/select/proxy_url')
def addrepo_proxy_url_check(element, app_node, local_node):
    proxy_url = get_attr(element, "value")
    return additional_repo_proxy_url(local_node, proxy_url, True)

@handle_act('/select/proxy_username')
def addrepo_proxy_url_username_handler(element, app_node, local_node):
    username = get_attr(element, "value")
    return additional_repo_proxy_username(local_node, username, False)

@handle_chck('/select/proxy_username')
def addrepo_proxy_url_username_check(element, app_node, local_node):
    username = get_attr(element, "value")
    return additional_repo_proxy_username(local_node, username, True)

@handle_act('/select/proxy_password')
def addrepo_proxy_url_password_handler(element, app_node, local_node):
    password = get_attr(element, "value")
    return additional_repo_proxy_password(local_node, password, False)

@handle_chck('/select/proxy_password')
def addrepo_proxy_url_password_chck(element, app_node, local_node):
    password = get_attr(element, "value")
    return additional_repo_proxy_password(local_node, password, True)

def add_repo_manipulate(element, app_node, local_node, dry_run):
    repo_name = get_attr(element, "name")
    repo_url = get_attr(element, "url")
    url_type = get_attr(element, "url_type")
    url_protocol = get_attr(element, "url_protocol")
    proxy_url = get_attr(element, "proxy_url")
    proxy_username = get_attr(element, "proxy_username")
    proxy_password = get_attr(element, "proxy_password")
    repo_enabled = get_attr_bool(element, "enabled", True)

    try:
        toolbox = getnode(local_node, "tool bar")
    except TimeoutError:
        return NotFound("tool bar")
    try:
        add_btn = getnode(toolbox, "push button", tr("A_dd", context="GUI|Software Source"))
    except TimeoutError:
        return NotFound("add repo button")
    if not dry_run:
        add_btn.click()

    def handler_msg(func, *args, **kwargs):
        action_type = "check" if dry_run else "action"
        result = func(*args, **kwargs)
        result_msg = "PASS" if result else "FAIL: %s" % result.reason
        logger.info("Executed individual %s handler for additional repo %s with result: %s", action_type, func.__name__, result_msg)
        return result

    results = []
    default_protocol = False
    if repo_name is not None:
        results.append(handler_msg(additional_repo_name, local_node, repo_name, dry_run))
    if repo_url is not None:
        url_match = re.match(r"((https?|ftp)://|nfs:)(.*)", repo_url)
        if dry_run and url_match and url_protocol:
            logger.warn("URL contains the protocol part AND the protocol has been specified explicitly - will only check the explicit one (%s)" %
                url_protocol)
            repo_url = url_match.group(3)
        elif not url_protocol:
            repo_url = url_match.group(3)    
            url_protocol = url_match.group(1)
            default_protocol = True
            logger.info("URL protocol not specified explicitly, only the implicit protocol (%s) will be checked." % url_protocol)
        results.append(handler_msg(additional_repo_url, local_node, repo_url, dry_run))

    results.append(handler_msg(addrepo_status, local_node, repo_enabled, dry_run))
    if (url_protocol is not None and not default_protocol) or (default_protocol and dry_run):
        results.append(handler_msg(additional_repo_url_protocol, app_node, local_node, url_protocol, dry_run))
    if url_type is not None:
        results.append(handler_msg(additional_repo_url_type, app_node, local_node, url_type, dry_run))
    if proxy_url is not None:
        results.append(handler_msg(additional_repo_proxy_url, local_node, proxy_url, dry_run))
    if proxy_username is not None:
        results.append(handler_msg(additional_repo_proxy_username, local_node, proxy_username, dry_run))
    if proxy_password is not None:
        results.append(handler_msg(additional_repo_proxy_password, local_node, proxy_password, dry_run))
    infobar_message_result = check_infobar_message(app_node)
    if infobar_message_result:
        results.append(infobar_message_result)

    if all(map(lambda x: isinstance(x, Pass), results)):
        return PASS
    else:
        return Fail("One or more failures in individual handlers, see FAIL message(s) above.")

@handle_act('/add')
def add_repo_handler(element, app_node, local_node):
    return add_repo_manipulate(element, app_node, local_node, False)

@handle_chck('/add')
def add_repo_check(element, app_node, local_node):
    repo_name = get_attr(element, "name", r"New_Repository(_\d+)?")
    try:
        repo_table = getnode(local_node, "table")
        repo_cells = getnodes(repo_table, "table cell")[1::2]
    except TimeoutError:
        return NotFound("repo table or repo cells")
    selected_repo = [cell for cell in repo_cells if cell.selected][0].name
    if re.match(repo_name, selected_repo):
        return add_repo_manipulate(element, app_node, local_node, True)
    else:
        return Fail("New repository hasn't been added or has unknown name.")

@handle_act('/reset')
def addrepo_reset_handler(element, app_node, local_node):
    try:
        revert_button = getnode(local_node, "push button", tr("Rese_t", context=source_context))
    except TimeoutError:
        return NotFound("revert button")
    revert_button.click()
    return PASS

@handle_chck('/reset')
def addrepo_reset_check(element, app_node, local_node):
    if get_repolist(local_node) == initial_repos:
        return PASS
    else:
        return Fail("Repo names and statuses haven't returned back to the initial state after reset.")