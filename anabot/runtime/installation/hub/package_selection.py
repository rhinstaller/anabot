# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getparent, getsibling
from anabot.runtime.comps import reload_comps, get_comps
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, comps_tr_env, comps_tr_group, comps_tr_env_desc, comps_tr_group_desc, comps_tr_env_rev

_local_path = '/installation/hub/package_selection'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    spoke_selector = getnode(local_node, "spoke selector",
                             tr("_SOFTWARE SELECTION", context="GUI|Spoke"))
    reload_comps()
    spoke_selector.click()
    spoke_label = getnode(app_node, "label", tr("SOFTWARE SELECTION"))
    local_node = getparent(spoke_label, "filler")
    default_handler(element, app_node, local_node)
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()

@handle_chck('')
def base_check(element, app_node, local_node):
    pass

def env_list_node(local_node):
    return getnode(local_node, "list box")

@handle_act('/environment')
def environment_handler(element, app_node, local_node):
    env_id = get_attr(element, "id")
    if env_id is not None:
        env_label_text = comps_tr_env(env_id)+"\n"+comps_tr_env_desc(env_id)
        logger.debug("Using environment label: %s", env_label_text)
    # group list is first list box
    env_list = env_list_node(local_node)
    env_label = getnode(env_list, "label", env_label_text)
    env_radio = getsibling(env_label, -1, "radio button")
    env_radio.click()

@handle_chck('/environment')
def environment_check(element, app_node, local_node):
    pass

def current_env(local_node):
    comps = get_comps()
    env_list = env_list_node(local_node)
    selected = [e for e in getnodes(env_list, "radio button") if e.checked][0]
    env_name = getsibling(selected, 1, "label").text.split("\n")[0]
    return comps_tr_env_rev(env_name)

@handle_act('/addon')
def addon_handler(element, app_node, local_node):
    comps = get_comps()
    env = current_env(local_node)
    logger.debug("Current environment is: %s", env)
    check = get_attr(element, "action", "select") == "select"
    group_match = get_attr(element, "id")
    for group_id in [g for g in comps.groups_list(env) if fnmatchcase(g, group_match)]:
        group_label_text = comps_tr_group(group_id)+"\n"+comps_tr_group_desc(group_id)
        logger.debug("Using group label: %s", group_label_text)
        # group list is second list box
        group_list = getnodes(local_node, "list box")[1]
        group_label = getnode(group_list, "label", group_label_text)
        group_checkbox = getsibling(group_label, -1, "check box")
        if group_checkbox.checked != check:
            group_checkbox.click()

@handle_chck('/addon')
def addon_check(element, app_node, local_node):
    pass
