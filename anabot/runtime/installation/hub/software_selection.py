# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getparent, getsibling
from anabot.runtime.comps import reload_comps, get_comps
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, comps_tr_env, comps_tr_group, comps_tr_env_desc, comps_tr_group_desc, comps_tr_env_rev

_local_path = '/installation/hub/software_selection'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    try:
        spoke_selector = getnode(
            local_node, "spoke selector",
            tr("_SOFTWARE SELECTION", context="GUI|Spoke"),
            timeout=300,
        )
    except TimeoutError:
        return (False, "Couldn't find software selection in hub.")
    reload_comps()
    spoke_selector.click()
    try:
        spoke_label = getnode(app_node, "label", tr("SOFTWARE SELECTION"))
        local_node = getparent(spoke_label, "filler")
    except TimeoutError:
        return (False, 'Couldn\'t find software selection spoke.')
    default_handler(element, app_node, local_node)
    try:
        done_button = getnode(local_node, "push button", tr("_Done", False))
        done_button.click()
    except TimeoutError:
        return (False, 'Couldn\'t find "Done" button.')
    return True

@handle_chck('')
def base_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    try:
        spoke_label = getnode(app_node, "label", tr("SOFTWARE SELECTION"), visible=False)
        return True
    except TimeoutError:
        return (False, "Software selection spoke is still visible.")

def env_list_node(local_node):
    return getnode(local_node, "list box")

def current_env(local_node):
    comps = get_comps()
    env_list = env_list_node(local_node)
    selected = [e for e in getnodes(env_list, "radio button") if e.checked][0]
    env_name = getsibling(selected, 1, "label").text.split("\n")[0]
    return comps_tr_env_rev(env_name)

def environment_manipulate(element, app_node, local_node, dry_run):
    env_id = get_attr(element, "id")
    if env_id is not None:
        env_name = comps_tr_env(env_id)
        env_label_text = env_name+"\n"+comps_tr_env_desc(env_id)
        logger.debug("Using environment label: %s", env_label_text)
    # group list is first list box
    env_list = env_list_node(local_node)
    try:
        env_label = getnode(env_list, "label", env_label_text)
    except TimeoutError:
        return (False, 'Couldn\'t find environment: %s' % env_id)
    env_radio = getsibling(env_label, -1, "radio button")
    if not dry_run:
        env_radio.click()
    else:
        return env_radio.checked

@handle_act('/environment')
def environment_handler(element, app_node, local_node):
    return environment_manipulate(element, app_node, local_node, False)

@handle_chck('/environment')
def environment_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    return environment_manipulate(element, app_node, local_node, True)

def addon_handler_manipulate(element, app_node, local_node, dry_run):
    comps = get_comps()
    try:
        env = current_env(local_node)
    except TimeoutError:
        return (False, "Couldn't determine which environment is currently selected")
    logger.debug("Current environment is: %s", env)
    check = get_attr(element, "action", "select") == "select"
    group_match = get_attr(element, "id")
    result = check
    try:
        # group list is second list box
        group_list = getnodes(local_node, "list box")[1]
    except TimeoutError:
        return (False, 'Couldn\'t find list of groups')
    found = False
    for group_id in [g for g in comps.groups_list(env) if fnmatchcase(g, group_match)]:
        found = True
        group_label_text = comps_tr_group(group_id)+"\n"+comps_tr_group_desc(group_id)
        logger.debug("Using group label: %s", group_label_text)
        try:
            group_label = getnode(group_list, "label", group_label_text)
        except TimeoutError:
            reporter.log_fail("Couldn't find label for group: %s" % group_id)
            result = not check
            continue
        group_checkbox = getsibling(group_label, -1, "check box")
        if group_checkbox.checked != check:
            if not dry_run:
                group_checkbox.click()
            else:
                result = not check
    if not found:
        return (False, "Desired groups (%s) are not available for current environment (%s)." % (group_match, env))
    if result != check:
        return (False, "Not all desired groups were (de)selected.")
    return True

@handle_act('/addon')
def addon_handler_check(element, app_node, local_node):
    return addon_handler_manipulate(element, app_node, local_node, False)

@handle_chck('/addon')
def addon_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    return addon_handler_manipulate(element, app_node, local_node, True)
