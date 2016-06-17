import logging
logger = logging.getLogger('anabot')

from random import randint

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getsibling
from anabot.runtime.functions import getparents, TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.translate import oscap_tr as oscap_tr_
from anabot.runtime.actionresult import ActionResultPass
import re

_local_path = '/installation/hub/oscap_addon'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
_chosen_profile = None
_selected_profile = None

# temporary workaround for broken translation
def oscap_tr(intext, drop_underscore=True):
    if drop_underscore:
        return intext.replace("_", "")
    else:
        return intext

@handle_act('')
def base_handler(element, app_node, local_node):
    try:
        oscap_addon = getnode(app_node, "spoke selector",
                              oscap_tr("SECURITY POLICY"))
        oscap_addon.click()
    except TimeoutError:
        return (False, "Couldn't find \"SECURITY POLICY\" spoke selector")
    try:
        oscap_addon_label = getnode(app_node, "label",
                                    oscap_tr("SECURITY POLICY"))
    except TimeoutError:
        return (False, "Couldn't find \"SECURITY POLICY\" label")
    try:
        oscap_addon_panel = getparents(oscap_addon_label,
                                       predicates={'roleName': 'panel'})[2]
    except TimeoutError:
        return (False, "Couldn't find OSCAP addon panel")

    default_handler(element, app_node, oscap_addon_panel)

@handle_chck('')
def base_check(element, app_node, local_node):
    expected_message = get_attr(element, "expected_message")
    expected_message = oscap_tr_(expected_message)
    result = action_result(element, ActionResultPass())
    ok_status = {oscap_tr_("Everything okay"),
                 oscap_tr_("No profile selected"),
                 oscap_tr_("No content found")}
    if not result:
        return result

    try:
        oscap_addon_selector = getnode(app_node, "spoke selector",
                                       oscap_tr("SECURITY POLICY"))
    except TimeoutError:
        return(False, "Couldn't find OSCAP addon selector button")
    try:
        oscap_addon_status = getnode(oscap_addon_selector, "label").text.decode("utf-8")
    except TimeoutError:
        return(False,
               "Couldn't find status label on OSCAP addon selector button")
    if expected_message is None:
        if oscap_addon_status in ok_status:
            result = True
        else:
            result = (False, "Found error message in OSCAP addon selector "
                             "button: %s" % oscap_addon_status)
    else:
        if (oscap_addon_status in ok_status
                and oscap_addon_status == expected_message):
            return True
        else:
            logger.info("Expected status message: %s" % expected_message)
            return (False, "Wrong OSCAP addon selector status message: %s"
                    % oscap_addon_status)

def choose_manipulate(element, app_node, local_node, dryrun):
    mode = get_attr(element, "mode", "manual")
    try:
        profiles_label = getnode(local_node, "label",
                                 oscap_tr("Choose profile below:"))
    except TimeoutError:
        return (False, "Couldn't find \"Choose profile below:\" label")
    try:
        profiles_table = getsibling(profiles_label, 1, "table")
    except TimeoutError:
        return (False, "Couldn't find profiles table.")
    try:
        available_profiles = [p for p in getnodes(profiles_table, "table cell")
                              if p.text]
    except TimeoutError:
        return (False, "Couldn't find profiles (table cells)")
    profile = None # profile to be selected

    # selected profile needs to be remembered before selecting another one
    # because of check for random_strict mode
    selected_profile = [p for p in available_profiles if p.selected and p.text]
    global _chosen_profile
    if not dryrun:
        if len(selected_profile) == 0:
            _chosen_profile = None
        else:
            _chosen_profile = selected_profile[0]

    if mode == "manual":
        profile_name = get_attr(element, "profile")
        try:
            profile = [p for p in available_profiles
                       if p.name.splitlines()[0] == profile_name][0]
        except IndexError:
            return (False, "Couldn't find profile \"%s\"." % profile_name)
    elif mode == "random":
        profile = available_profiles[randint(0, len(available_profiles) - 1)]
    # choose a random profile other than already selected
    elif mode == "random_strict":
        if len(available_profiles) > 1:
            if len(selected_profile) == 0:
                profile = available_profiles[
                    randint(0, len(available_profiles) - 1)]
            elif len(selected_profile) == 1:
                profile_no = available_profiles.index(selected_profile[0])
                while (profile == None
                       or profile_no == available_profiles.index(profile)):
                    profile = available_profiles[
                        randint(0, len(available_profiles) - 1)]
        else:
            profile = available_profiles[0]
    else:
        return (False, "Unknown selection mode: %s" % mode)

    if dryrun:
        result = action_result(element, ActionResultPass())
        if not result:
            return result
        if mode == "manual":
            if not profile.selected:
                result = (False, "Profile %s hasn't been chosen."
                          % profile.name)
        elif mode == "random":
            if not any([p.selected for p in available_profiles]):
                result = (False, "No profile has been chosen.")
        elif mode == "random_strict":
            if not any([p.selected for p in available_profiles
                        if p is not _chosen_profile]):
                result = (False, "Profile choice hasn't changed.")
        return result
    else:
        global _selected_profile
        _selected_profile = profile
        profile.click()

@handle_act('/choose')
def choose_handler(element, app_node, local_node):
    return choose_manipulate(element, app_node, local_node, False)

@handle_chck('/choose')
def choose_check(element, app_node, local_node):
    return choose_manipulate(element, app_node, local_node, True)

@handle_act('/select')
def select_handler(element, app_node, local_node):
    try:
        select_button = getnode(local_node, "push button",
                                oscap_tr("_Select profile"),
                                sensitive=None)
    except TimeoutError:
        return (False, "Couldn't find \"Select profile\" button.")
    select_button.click()

@handle_chck('/select')
def select_check(element, app_node, local_node):
    try:
        select_button = getnode(local_node, "push button",
                                oscap_tr("_Select profile"),
                                sensitive=False)
    except TimeoutError:
        return (False, "Couldn't find sensitive \"Select profile\" button.")

    if _selected_profile is None:
        result = (False, "No profile has been selected.")
    elif select_button.sensitive:
        result = (False, "\"Select profile\" button is sensitive.")
    elif not _selected_profile.selected:
        result = (False, "Profile \"%s\" hasn't been selected." %
                  _selected_profile.name.splitlines()[0])
    else:
        result = True
    return result

def change_content_manipulate(element, app_node, local_node, dryrun):
    try:
        change_button = getnode(local_node, "push button",
                                oscap_tr("_Change content"))
    except TimeoutError:
        if dryrun:
            try:
                getnode(app_node, "spoke selector", oscap_tr("SECURITY POLICY"))
                logger.info("Detected that hub is active.")
                return True
            except TimeoutError:
                return (False, "Couldn't find neither \"_Change content\" "
                        "button (OSCAP spoke) nor OSCAP spoke selector (hub).")
        return (False, "Couldn't find \"_Change content\" button.")
    if dryrun:
        return action_result(element, ActionResultPass())
    else:
        change_button.click()
        try:
            getnode(local_node, "push button",
                    oscap_tr("_Use SCAP Security Guide"))
        except TimeoutError:
            return (False, "Couldn't find \"Use SCAP Security Guide\" button.")
        default_handler(element, app_node, local_node)

@handle_act('/change_content')
def change_content_handler(element, app_node, local_node):
    return change_content_manipulate(element, app_node, local_node, False)

@handle_chck('/change_content')
def change_content_check(element, app_node, local_node):
    result = action_result(element, ActionResultPass())
    if result:
        result = change_content_manipulate(element, app_node, local_node, True)
    return result

def change_content_source_manipulate(element, app_node, local_node, dryrun):
    try:
        fetch_button = getnode(local_node, "push button", oscap_tr("_Fetch"))
    except TimeoutError:
        return (False, "Couldn't find \"_Fetch\" button")
    try:
        datastream_url_input = getsibling(fetch_button, -1, "text")
    except TimeoutError:
        return (False, "Couldn't find URL input box.")
    url = get_attr(element, "url")
    if dryrun:
        return datastream_url_input.text == url
    else:
        datastream_url_input.typeText(url)

@handle_act('/change_content/source')
def change_content_source_handler(element, app_node, local_node):
    return change_content_source_manipulate(element, app_node,
                                            local_node, False)

@handle_chck('/change_content/source')
def change_content_source_check(element, app_node, local_node):
    return change_content_source_manipulate(element, app_node,
                                            local_node, True)

@handle_act('/change_content/fetch')
def change_content_fetch_handler(element, app_node, local_node):
    try:
        fetch_button = getnode(app_node, "push button", oscap_tr("_Fetch"))
    except TimeoutError:
        return (False, "Couldn't find \"_Fetch\" button.")
    fetch_button.click()

@handle_chck('/change_content/fetch')
def change_content_fetch_check(element, app_node, local_node):
    global _selected_profile
    result = action_result(element, ActionResultPass())
    if result:
        try:
            getnode(local_node, "push button", oscap_tr("_Change content"))
            result = True
            _selected_profile = None
        except TimeoutError:
            try:
                infobar = getnode(local_node, "info bar",
                                  predicates={"name": tr("Error")})
            except TimeoutError:
                result = (False, "Couldn't find info bar.")
            try:
                error = getnode(infobar, "label").text
                url = get_attr(element, "url")
                result = (False, "SCAP content fetch error: \"%s\", URL: %s"
                          % (error, url))
            except TimeoutError:
                result = (False, "Couldn't find message label in info bar.")
    return result

@handle_act('/change_content/use_ssg')
def change_content_use_ssg_handler(element, app_node, local_node):
    global _selected_profile
    try:
        use_ssg_button = getnode(local_node, "push button",
                                 oscap_tr("_Use SCAP Security Guide"))
        use_ssg_button.click()
        _selected_profile = None
    except TimeoutError:
        return (False, "Couldn't find \"Use SCAP Security Guide\" button.")

@handle_chck('/change_content/use_ssg')
def change_content_use_ssg_check(element, app_node, local_node):
    result = action_result(element, ActionResultPass())
    if result:
        try:
            getnode(local_node, "push button",
                    oscap_tr("_Use SCAP Security Guide"), visible=False)
            result = True
        except TimeoutError:
            result = (False, "Couldn't find \"Use SCAP Security Guide\" "
                      "button.")
    return result

def apply_policy_manipulate(element, app_node, local_node, dryrun):
    policy_action = get_attr(element, "action")
    try:
        apply_policy_label = getnode(local_node, "label",
                                     oscap_tr("Apply security policy:"))
    except TimeoutError:
        return (False, "Couldn't find \"Apply security policy:\" label")
    try:
        policy_button = getsibling(apply_policy_label, 1, "toggle button")
    except TimeoutError:
        return (False, "Couldn't find policy on/off switch.")

    if dryrun:
        return (policy_action == "enable" and policy_button.checked
                or policy_action == "disable" and not policy_button.checked)
    else:
        if (policy_action == "enable" and not policy_button.checked or
                policy_action == "disable" and policy_button.checked):
            policy_button.click()

@handle_act('/apply_policy')
def apply_policy_handler(element, app_node, local_node):
    return apply_policy_manipulate(element, app_node, local_node, False)

@handle_chck('/apply_policy')
def apply_policy_check(element, app_node, local_node):
    return apply_policy_manipulate(element, app_node, local_node, True)

def datastream_manipulate(element, app_node, local_node, dryrun):
    global _selected_profile
    datastream = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    try:
        ds_label = getnode(local_node, "label", oscap_tr("Data stream:"))
    except TimeoutError:
        return (False, "Couldn't find \"Data stream:\" label")
    try:
        ds_combo = getsibling(ds_label, 1, "combo box")
    except TimeoutError:
        return (False, "Couldn't find data stream combo box")
    if not dryrun:
        ds_combo.click()
        try:
            ds_items = getnodes(ds_combo, "menu item")
        except TimeoutError:
            return (False, "Couldn't find data stream menu items.")
    if dryrun:
        result = action_result(element, ActionResultPass())
        if not result:
            return result
        if mode == "random":
            result = ds_combo.name != ""
        elif mode == "manual":
            result = ds_combo.name == datastream
        return result
    else:
        current_ds = ds_combo.name
        if mode == "manual":
            try:
                ds_item = getnode(ds_combo, "menu item", datastream)
            except TimeoutError:
                ds_combo.click()
                return (False, "Data stream '%s' not found" % datastream)
        elif mode == "random":
            ds_item = ds_items[randint(0, len(ds_items) - 1)]
        ds_item.click()
        if current_ds != ds_combo.name:
            _selected_profile = None

@handle_act('/select_datastream')
def datastream_handler(element, app_node, local_node):
    return datastream_manipulate(element, app_node, local_node, False)

@handle_chck('/select_datastream')
def datastream_chck(element, app_node, local_node):
    return datastream_manipulate(element, app_node, local_node, True)

def checklist_manipulate(element, app_node, local_node, dryrun):
    global _selected_profile
    checklist = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    try:
        checklist_label = getnode(local_node, "label", oscap_tr("Checklist:"))
    except TimeoutError:
        return (False, "Couldn't find \"Checklist:\" label")
    try:
        checklist_combo = getsibling(checklist_label, 1, "combo box")
    except TimeoutError:
        return (False, "Couldn't find checklist  combo box")
    if not dryrun:
        try:
            checklist_combo.click()
            checklist_items = getnodes(checklist_combo, "menu item")
        except TimeoutError:
            return (False, "Couldn't find checklist menu items")

    if dryrun:
        result = action_result(element, ActionResultPass())
        if not result:
            return result
        if mode == "manual":
            datastream = get_attr(element, "id")
            try:
                checklist_label = getnode(local_node, "label",
                                          oscap_tr("Checklist:"))
            except TimeoutError:
                return (False, "Couldn't find \"Checklist:\" label")
            try:
                checklist_combo = getsibling(checklist_label, 1, "combo box")
            except TimeoutError:
                return (False, "Couldn't find checklist combo box.")
            result = checklist_combo.name == datastream
        elif mode == "random":
            result = checklist_combo.name != ""
        return result
    else:
        current_checklist = checklist_combo.name
        if mode == "manual":
            try:
                checklist_item = getnode(checklist_combo, "menu item",
                                         checklist)
            except TimeoutError:
                checklist_combo.click()
                return(False, "Checklist \"%s\" not found" % checklist)
        elif mode == "random":
            checklist_item = checklist_items[
                randint(0, len(checklist_items) - 1)]
        else:
            return (False, "Unknown mode: \"%s\"" % mode)
        checklist_item.click()
        if checklist_combo.name != current_checklist:
            _selected_profile = None

@handle_act('/select_checklist')
def checklist_handler(element, app_node, local_node):
    return checklist_manipulate(element, app_node, local_node, False)

@handle_chck('/select_checklist')
def checklist_check(element, app_node, local_node):
    return checklist_manipulate(element, app_node, local_node, True)

@handle_act('/changes')
def changes_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/changes')
def changes_check(element, app_node, local_node):
    return True

@handle_act('/changes/info')
@handle_act('/changes/warning')
@handle_act('/changes/error')
def changes_line_handler(element, app_node, local_node):
    # TODO: implement separate info/warning/error handlers when/if it becomes
    # possible to recognize the different message types through ATK
    if element in {'/changes/info', '/changes/warning', '/changes/error'}:
        logger.warn("Specialized handler for %s not available, using "
                    "generic one.", element)

@handle_chck('/changes/info')
@handle_chck('/changes/warning')
@handle_chck('/changes/error')
def changes_line_check(element, app_node, local_node):
    raw_text = get_attr(element, "text")
    params = get_attr(element, "params")
    if params is not None:
        params = tuple(params.split())
    # ugly workaround for broken translations:
    if raw_text == "No rules for the pre-installation phase":
        translated_text = oscap_tr_(raw_text)
    else:
        translated_text = raw_text

    # regex is not 100% accurate, but should be sufficient for these purposes
    translated_text = re.sub(r'%((\(\w+\)(\d+\.)?\d*\w)|(\d+\.)?\d*\w)', '%s',
                             translated_text)
    if params is not None:
        translated_text = translated_text % params
    try:
        changes_label = getnode(local_node, "label",
                                oscap_tr("Changes that were done or need "
                                         "to be done:"))
    except TimeoutError:
        return(False, "Couldn't find \"Changes that were done...\" label")
    try:
        changes_table = getsibling(changes_label, 1, "table")
    except TimeoutError:
        return(False, "Couldn't find table with changes.")
    try:
        getnode(changes_table, "table cell",
                predicates={"name": translated_text})
        return True
    except TimeoutError:
        return (False,
                "Couldn't find line \"%s\" in changes table."
                % translated_text)

@handle_act('/done')
@handle_act('/change_content/done')
def done_handler(element, app_node, local_node):
    try:
        done_button = getnode(local_node, "push button", tr("_Done", False))
    except TimeoutError:
        return (False, "Couldn't find \"Done\" button.")
    done_button.click()

@handle_chck('/done')
@handle_chck('/change_content/done')
def done_check(element, app_node, local_node):
    result = action_result(element, ActionResultPass())
    if result:
        try:
            getnode(app_node, "spoke selector", oscap_tr("SECURITY POLICY"))
        except TimeoutError:
            return(False, "OSCAP addon selector button not found.")
    return result

