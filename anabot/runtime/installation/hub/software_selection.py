# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

import random
from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getnodes, getparent, getsibling, disappeared
from anabot.runtime.comps import reload_comps, get_comps
from anabot.runtime.hooks import register_post_hook
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, comps_tr_env, comps_tr_group, comps_tr_env_desc, comps_tr_group_rev, comps_tr_group_desc, comps_tr_env_rev

_local_path = '/installation/hub/software_selection'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

__selected_environment = None
__selected_addons = None

PACKAGE_SELECTION_STORE = '/mnt/sysimage/root/anabot-packageset.txt'
@register_post_hook(None)
def record_package_selection():
    if __selected_environment is None and __selected_addons is None:
        return
    reporter.log_info('Saving package selection to %s'%PACKAGE_SELECTION_STORE)
    addons_in_env = get_comps().mandatory_groups_list(__selected_environment)
    addons = __selected_addons + addons_in_env
    with open(PACKAGE_SELECTION_STORE, 'w') as outfile:
        outfile.write("@^" + __selected_environment + "\n")
        for addon in addons:
            outfile.write("@" + addon + "\n")

def random_sublist(inlist):
    return [x for x in inlist if random.choice((True, False))]

@handle_act('')
def base_handler(element, app_node, local_node):
    global __selected_environment
    global __selected_addons
    save_selection = get_attr(element, "save-selection", "no") == "yes"
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
    # save information about selected package selection
    if save_selection:
        __selected_environment = current_env(local_node)
        __selected_addons = current_addons(local_node)
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
    if disappeared(app_node, "push button", tr("_Done", False)):
        return True
    else:
        return (False, "Done button (probably in software selection spoke) is still visible.")

def env_list_node(local_node):
    # env list is first list box
    return getnode(local_node, "list box")

def current_env(local_node):
    comps = get_comps()
    env_list = env_list_node(local_node)
    selected = [e for e in getnodes(env_list, "radio button") if e.checked][0]
    env_name = getsibling(selected, 1, "label").text.split("\n")[0]
    return comps_tr_env_rev(env_name)

def addons_list_node(local_node):
    # addon list is second list box
    return getnodes(local_node, "list box")[1]

def current_addons(local_node):
    groups_list = []
    comps = get_comps()
    addons_list = addons_list_node(local_node)
    for group_checkbox in getnodes(addons_list, "check box", visible=None):
        if not group_checkbox.checked:
            continue
        group_name = getsibling(
            group_checkbox, 1, "label", visible=None
        ).text.split("\n")[0]
        groups_list.append(comps_tr_group_rev(group_name))
    return groups_list

__last_random_env = None
def environment_manipulate(element, app_node, local_node, dry_run):
    global __last_random_env
    # define in schema, that id and select attributes conflict
    # define in schema, that just_check* conflicts with select=random
    env_id = get_attr(element, "id")
    select = get_attr(element, "select")
    if select == "random":
        if dry_run:
            env_id = __last_random_env
        else:
            env_id = random.choice(get_comps().env_list())
            __last_random_env = env_id
    if env_id is not None:
        env_name = comps_tr_env(env_id)
        if env_name is None:
            return (False, 'Specified environment is not known: %s' % env_id)
        env_label_text = env_name+"\n"+comps_tr_env_desc(env_id)
        logger.debug("Using environment label: %s", env_label_text)
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

__last_random_addons = None
def addon_handler_manipulate(element, app_node, local_node, dry_run):
    global __last_random_addons
    comps = get_comps()
    try:
        env = current_env(local_node)
    except TimeoutError:
        return (False, "Couldn't determine which environment is currently selected")
    logger.debug("Current environment is: %s", env)
    check = get_attr(element, "action", "select") == "select"
    group_match = get_attr(element, "id")
    group_ids = [g for g in comps.groups_list(env) if fnmatchcase(g, group_match)]
    subselect = get_attr(element, "subselect")
    if subselect == "random":
        # define in schema, that just_check* conflicts with subselect=random
        if dry_run:
            group_ids = __last_random_addons
        else:
            group_ids = random_sublist(group_ids)
            __last_random_addons = group_ids
    result = check
    try:
        group_list = addons_list_node(local_node)
    except TimeoutError:
        __last_random_addons = None
        return (False, 'Couldn\'t find list of groups')
    found = False
    for group_id in group_ids:
        logger.debug("Processing group with id: %s", group_id)
        found = True
        group_label_text = comps_tr_group(group_id)+"\n"+comps_tr_group_desc(group_id)
        logger.debug("Using group label: %s", group_label_text)
        try:
            group_label = getnode_scroll(group_list, "label", group_label_text)
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
    if dry_run:
        __last_random_addons = None
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
