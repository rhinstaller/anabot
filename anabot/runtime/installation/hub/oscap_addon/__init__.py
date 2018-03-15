import logging
logger = logging.getLogger('anabot')

import random

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.decorators import check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getsibling
from anabot.runtime.functions import getnode_scroll, scrollto
from anabot.runtime.functions import getparents, TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.translate import oscap_tr as oscap_tr_
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound
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


SPOKE_SELECTOR_NF = NotFound("active spoke selector",
                             "selector_not_found",
                             whose="OSCAP addon spoke")
SECURITY_POLICY_LABEL_NF = NotFound("\"SECURITY POLICY\" label",
                                    "label_not_found")
OSCAP_SPOKE_NF = NotFound("OSCAP addon panel", "spoke_not_found")
@handle_act('')
def base_handler(element, app_node, local_node):
    try:
        oscap_addon = getnode_scroll(app_node, "spoke selector",
                                     oscap_tr("SECURITY POLICY"))
        oscap_addon.click()
    except TimeoutError:
        return SPOKE_SELECTOR_NF
    try:
        oscap_addon_label = getnode(app_node, "label",
                                    oscap_tr("SECURITY POLICY"))
    except TimeoutError:
        return SECURITY_POLICY_LABEL_NF
    try:
        oscap_addon_panel = getparents(oscap_addon_label, "panel")[2]
    except TimeoutError:
        return OSCAP_SPOKE_NF

    default_handler(element, app_node, oscap_addon_panel)

SPOKE_SELECTOR_STATUS_NF = NotFound("OSCAP status label",
                                    "label_not_found",
                                    where="OSCAP spoke selector")
WRONG_SELECTOR_MESSAGE = Fail("OSCAP addon selector contained wrong message: "
                              "%s, expected: %s", "wrong_message")
@handle_chck('')
@check_action_result
def base_check(element, app_node, local_node):
    expected_message = get_attr(element, "expected_message")
    if expected_message is not None:
	expected_message = oscap_tr_(expected_message)
    OK_STATUS = {oscap_tr_("Everything okay"),
                 oscap_tr_("No profile selected"),
                 oscap_tr_("No content found")}
    FAIL_STATUS = {
        oscap_tr_("Not ready"): 'not_ready',
        oscap_tr_("Misconfiguration detected"): 'misconfiguration_detected',
        oscap_tr_("Warnings appeared"): 'warnings_appeared',
        oscap_tr_("Error fetching and loading content"): 'content_fetch_load_error'}

    try:
        oscap_addon_selector = getnode_scroll(app_node, "spoke selector",
                                              oscap_tr("SECURITY POLICY"))
    except TimeoutError:
        return SPOKE_SELECTOR_NF
    try:
        oscap_addon_status = getnode(oscap_addon_selector, "label").text.decode("utf-8")
    except TimeoutError:
        return SPOKE_SELECTOR_STATUS_NF

    if oscap_addon_status in OK_STATUS:
        if expected_message is None or oscap_addon_status == expected_message:
                return Pass()
        return WRONG_SELECTOR_MESSAGE % (oscap_addon_status, expected_message)
    return Fail("OSCAP addon selector check failed due to: %s" % oscap_addon_status,
                (FAIL_STATUS.get(oscap_addon_status, "unhandled_message")))

CHOOSE_PROFILE_LABEL_NF = NotFound("\"Choose profile below:\" label",
                                   "label_not_found")
PROFILES_PANE_NF = NotFound("scroll pane", fail_type="pane_not_found",
                            whose="profile list")
PROFILES_TABLE_NF = NotFound("profiles table", "table_not_found")
PROFILES_NF = NotFound("profiles (table cells)", "cells_not_found")
PROFILE_NF = NotFound("profile \"%s\"")
def choose_manipulate(element, app_node, local_node, dryrun):
    global _chosen_profile
    global _selected_profile
    mode = get_attr(element, "mode", "manual")
    try:
        profiles_label = getnode(local_node, "label",
                                 oscap_tr("Choose profile below:"))
    except TimeoutError:
        return CHOOSE_PROFILE_LABEL_NF
    try:
        profiles_pane = getsibling(profiles_label, 1, "scroll pane")
    except TimeoutError:
        return PROFILES_PANE_NF
    try:
        profiles_table = getnode(profiles_pane, "table")
    except TimeoutError:
        return PROFILES_TABLE_NF
    try:
        available_profiles = getnodes(profiles_table, "table cell",
                                      visible=None)[::2]
    except TimeoutError:
        return PROFILES_NF
    profile = None # profile to be selected

    # selected profile needs to be remembered before selecting another one
    # because of check for random_strict mode
    selected_profile = [p for p in available_profiles if p.selected and p.text]
    if not dryrun:
        if len(selected_profile) == 0:
            _chosen_profile = None
        else:
            _chosen_profile = selected_profile[0]

    if mode == "manual":
        profile_name = get_attr(element, "profile")
        try:
            profile = [p for p in available_profiles
                       if p.name.startswith(profile_name + '\n')][0]
        except IndexError:
            return PROFILE_NF % profile_name
    elif mode == "random":
        profile = random.choice(available_profiles)
    # choose a random profile other than already selected
    elif mode == "random_strict":
        if len(available_profiles) > 1:
            if len(selected_profile) == 0:
                profile = random.choice(available_profiles)
            elif len(selected_profile) == 1:
                profile_no = available_profiles.index(selected_profile[0])
                while (profile == None
                       or profile_no == available_profiles.index(profile)):
                    profile = random.choice(available_profiles)
        else:
            profile = available_profiles[0]
    else:
        return Fail("Unknown selection mode: %s" % mode)

    if dryrun:
        result = Pass()
        if mode == "manual":
            if not profile.selected:
                return Fail("Profile %s hasn't been chosen." % profile.name)
        elif mode == "random":
            if not any([p.selected for p in available_profiles]):
                return Fail("No profile has been chosen.")
        elif mode == "random_strict":
            if not any([p.selected for p in available_profiles
                        if p is not _chosen_profile]):
                return Fail("Profile choice hasn't changed.")
        return result
    else:
        scrollto(profile)
        _selected_profile = profile
        profile.click()

@handle_act('/choose')
def choose_handler(element, app_node, local_node):
    return choose_manipulate(element, app_node, local_node, False)

@handle_chck('/choose')
@check_action_result
def choose_check(element, app_node, local_node):
    return choose_manipulate(element, app_node, local_node, True)

SELECT_PROFILE_BUTTON_NF = NotFound("sensitive \"Select profile\" button.",
                                    "button_not_found")
@handle_act('/select')
def select_handler(element, app_node, local_node):
    try:
        select_button = getnode(local_node, "push button",
                                oscap_tr("_Select profile"),
                                sensitive=None)
    except TimeoutError:
        return SELECT_PROFILE_BUTTON_NF
    select_button.click()

@handle_chck('/select')
@check_action_result
def select_check(element, app_node, local_node):
    try:
        select_button = getnode(local_node, "push button",
                                oscap_tr("_Select profile"),
                                sensitive=False)
    except TimeoutError:
        return SELECT_PROFILE_BUTTON_NF

    if _selected_profile is None:
        result = Fail("No profile has been selected.")
    elif select_button.sensitive:
        result = Fail("\"Select profile\" button is clickable.")
    elif not _selected_profile.selected:
        result = Fail("Profile \"%s\" hasn't been selected." %
                      _selected_profile.name.splitlines()[0])
    else:
        result = Pass()
    return result

CHANGE_CONTENT_BUTTON_NF = NotFound("\"_Change content\" button",
                                    "button_not_found")
SCAP_SECURITY_GUIDE_BUTTON_NF = NotFound("\"Use SCAP Security Guide\" button",
                                         "button_not_found")
def change_content_manipulate(element, app_node, local_node, dryrun):
    try:
        change_button = getnode(local_node, "push button",
                                oscap_tr("_Change content"))
    except TimeoutError:
        if dryrun:
            try:
                getnode_scroll(app_node, "spoke selector", oscap_tr("SECURITY POLICY"))
                logger.info("Detected that hub is active.")
                return Pass()
            except TimeoutError:
                return NotFound("\"_Change content\" button (OSCAP spoke) "
                                "nor OSCAP spoke selector (hub).")
        return CHANGE_CONTENT_BUTTON_NF
    if dryrun:
        return action_result(element, Pass())
    else:
        change_button.click()
        try:
            getnode(local_node, "push button",
                    oscap_tr("_Use SCAP Security Guide"))
        except TimeoutError:
            return SCAP_SECURITY_GUIDE_BUTTON_NF
        default_handler(element, app_node, local_node)

@handle_act('/change_content')
def change_content_handler(element, app_node, local_node):
    return change_content_manipulate(element, app_node, local_node, False)

@handle_chck('/change_content')
@check_action_result
def change_content_check(element, app_node, local_node):
    return change_content_manipulate(element, app_node, local_node, True)

FETCH_BUTTON_NF = NotFound("\"_Fetch\" button", "button_not_found")
URL_INPUT_NF = NotFound("URL input box", "text_input_not_found")
def change_content_source_manipulate(element, app_node, local_node, dryrun):
    try:
        fetch_button = getnode(local_node, "push button", oscap_tr("_Fetch"))
    except TimeoutError:
        return FETCH_BUTTON_NF
    try:
        datastream_url_input = getsibling(fetch_button, -1, "text")
    except TimeoutError:
        return URL_INPUT_NF
    url = get_attr(element, "url")
    if dryrun:
        if datastream_url_input.text == url:
            return Pass()
        else:
            return Fail("URL input box contains wrong URL (%s), not "
                        "the expected one (%s)"
                        % (datastream_url_input.text, url))
    else:
        datastream_url_input.text = ""
        datastream_url_input.typeText(url)

@handle_act('/change_content/source')
def change_content_source_handler(element, app_node, local_node):
    return change_content_source_manipulate(element, app_node,
                                            local_node, False)

@handle_chck('/change_content/source')
@check_action_result
def change_content_source_check(element, app_node, local_node):
    return change_content_source_manipulate(element, app_node,
                                            local_node, True)

@handle_act('/change_content/fetch')
def change_content_fetch_handler(element, app_node, local_node):
    try:
        fetch_button = getnode(app_node, "push button", oscap_tr("_Fetch"))
    except TimeoutError:
        return FETCH_BUTTON_NF
    fetch_button.click()

INFO_BAR_NF = NotFound("info bar", "info_bar_not_found")
INFO_BAR_LABEL_NF = NotFound("message label", "label_not_found",
                             where="info bar")
ERROR_LABEL_NF = NotFound("content fetch error label", "label_not_found")
@handle_chck('/change_content/fetch')
@check_action_result
def change_content_fetch_check(element, app_node, local_node):
    global _selected_profile
    FAIL_MSG = {oscap_tr_("Invalid or unsupported URL"): 'invalid_url',
                oscap_tr_("No content found. Please enter data stream content "
                         "or archive URL below:"): 'no_content_found',
                oscap_tr_("Failed to extract content (%s). Enter a different "
                         "URL, please.") % ".*": 'extraction_failed',
                oscap_tr_("Failed to fetch content. Enter a different URL, "
                          "please."): 'fetch_failed',
                oscap_tr_("Invalid content provided. Enter a different URL, "
                          "please."): 'invalid_content',
                oscap_tr_("Network error encountered when fetching data."
                          " Please check that network is setup and "
                          "working."): 'network_error'}
    try:
        getnode(local_node, "push button", oscap_tr("_Change content"))
        return Pass()
        _selected_profile = None
    except TimeoutError:
        # retrieve URL so that it can be included in fail message
        try:
            fetch_button = getnode(local_node, "push button", oscap_tr("_Fetch"))
        except TimeoutError:
            return FETCH_BUTTON_NF
        try:
            url = getsibling(fetch_button, -1, "text").text
        except TimeoutError:
            return URL_INPUT_NF
        try:
            filler = getsibling(getparents(fetch_button)[0], 1, "filler")
            error_label = getnode(filler, "label")
        except TimeoutError:
            return ERROR_LABEL_NF

        try:
            infobar = getnode(local_node, "info bar", tr("Error"))
        except TimeoutError:
            return INFO_BAR_NF
        try:
            error = getnode(infobar, "label").text
        except TimeoutError:
            return INFO_BAR_LABEL_NF

        if error != error_label.text:
            return Fail("Message in error label (%s) differs from message "
                        "in info bar (%s)" % (error_label.text, error),
            "inconsistent_messages")

        for msg, fail_type in FAIL_MSG.iteritems():
            if re.match(msg, unicode(error)):
                break
        else:
            return Fail("Unhandled error message: %s" % error,
                        "unhandled_message")
        return Fail("SCAP content fetch error: \"%s\", URL: %s"
                    % (error, url), fail_type)

# 'Use Scap Security Guide' button in some cases can only be accessed
# directly from the 'root' OSCAP element (e. g. in KS installation with
# incorrect fingerprint specified)
@handle_act('/use_ssg')
@handle_act('/change_content/use_ssg')
def change_content_use_ssg_handler(element, app_node, local_node):
    global _selected_profile
    try:
        use_ssg_button = getnode(local_node, "push button",
                                 oscap_tr("_Use SCAP Security Guide"))
        use_ssg_button.click()
        _selected_profile = None
    except TimeoutError:
        return SCAP_SECURITY_GUIDE_BUTTON_NF

@handle_chck('/use_ssg')
@handle_chck('/change_content/use_ssg')
@check_action_result
def change_content_use_ssg_check(element, app_node, local_node):
    try:
        getnode(local_node, "push button",
                oscap_tr("_Use SCAP Security Guide"), visible=False)
        return Pass()
    except TimeoutError:
        return SCAP_SECURITY_GUIDE_BUTTON_NF

APPLY_SECURITY_POLICY_LABEL_NF = NotFound("\"Apply security policy:\" label",
                                          "label_not_found")
POLICY_SWITCH_NF = NotFound("policy on/off switch")
def apply_policy_manipulate(element, app_node, local_node, dryrun):
    policy_action = get_attr(element, "action")
    try:
        apply_policy_label = getnode(local_node, "label",
                                     oscap_tr("Apply security policy:"))
    except TimeoutError:
        return APPLY_SECURITY_POLICY_LABEL_NF
    try:
        policy_button = getsibling(apply_policy_label, 1, "toggle button")
    except TimeoutError:
        return POLICY_SWITCH_NF

    if dryrun:
        if (policy_action == "enable" and policy_button.checked
                or policy_action == "disable" and not policy_button.checked):
            return Pass()
        else:
            return Fail("SCAP policy switch state doesn't correspond with "
                        "required state (%s)" % policy_action)
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

DATASTREAM_LABEL_NF = NotFound("\"Data stream:\" label", "label_not_found")
DATASTREAM_COMBO_NF = NotFound("data stream combo box", "combo_box_not_found")
DATASTREAM_ITEMS_NF = NotFound("data stream menu items")
DATASTREAM_NF = NotFound("data stream '%s'")
def datastream_manipulate(element, app_node, local_node, dryrun):
    global _selected_profile
    datastream = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    try:
        ds_label = getnode(local_node, "label", oscap_tr("Data stream:"))
    except TimeoutError:
        return DATASTREAM_LABEL_NF
    try:
        ds_combo = getsibling(ds_label, 1, "combo box")
    except TimeoutError:
        return DATASTREAM_COMBO_NF
    if not dryrun:
        ds_combo.click()
        try:
            ds_items = getnodes(ds_combo, "menu item")
        except TimeoutError:
            return DATASTREAM_ITEMS_NF
        current_ds = ds_combo.name
        if mode == "manual":
            try:
                ds_item = getnode(ds_combo, "menu item", datastream)
            except TimeoutError:
                ds_combo.click()
                return DATASTREAM_NF
        elif mode == "random":
            ds_item = random.choice(ds_items)
        ds_item.click()
        if current_ds != ds_combo.name:
            _selected_profile = None
    else:
        if mode == "random":
            return Pass()
        elif mode == "manual":
            if ds_combo.name == datastream:
                return Pass()
            else:
                return Fail("Item selected in datastream combo box (%s) "
                            "doesn't match the required one (%s)"
                            % (ds_combo.name, datastream))
        else:
            return Fail("Unknown mode: %s" % mode)

@handle_act('/select_datastream')
def datastream_handler(element, app_node, local_node):
    return datastream_manipulate(element, app_node, local_node, False)

@handle_chck('/select_datastream')
@check_action_result
def datastream_chck(element, app_node, local_node):
    return datastream_manipulate(element, app_node, local_node, True)

CHECKLIST_LABEL_NF = NotFound("\"Checklist:\" label", "label_not_found")
CHECKLIST_COMBO_NF = NotFound("checklist combo box", "combo_box_not_found")
CHECKLIST_ITEMS_NF = NotFound("checklist menu items")
CHECKLIST_NF = NotFound("checklist \"%s\"")
def checklist_manipulate(element, app_node, local_node, dryrun):
    global _selected_profile
    checklist = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    try:
        checklist_label = getnode(local_node, "label", oscap_tr("Checklist:"))
    except TimeoutError:
        return CHECKLIST_LABEL_NF
    try:
        checklist_combo = getsibling(checklist_label, 1, "combo box")
    except TimeoutError:
        return CHECKLIST_LABEL_NF
    if not dryrun:
        try:
            checklist_combo.click()
            checklist_items = getnodes(checklist_combo, "menu item")
        except TimeoutError:
            return CHECKLIST_ITEMS_NF
        current_checklist = checklist_combo.name
        if mode == "manual":
            try:
                checklist_item = getnode(checklist_combo, "menu item",
                                         checklist)
            except TimeoutError:
                checklist_combo.click()
                return CHECKLIST_NF % checklist
        elif mode == "random":
            checklist_item = random.choice(checklist_items)
        else:
            return Fail("Unknown mode: \"%s\"" % mode)
        checklist_item.click()
        if checklist_combo.name != current_checklist:
            _selected_profile = None

    else:
        if mode == "manual":
            checklist = get_attr(element, "id")
            try:
                checklist_label = getnode(local_node, "label",
                                          oscap_tr("Checklist:"))
            except TimeoutError:
                return CHECKLIST_LABEL_NF
            try:
                checklist_combo = getsibling(checklist_label, 1, "combo box")
            except TimeoutError:
                return CHECKLIST_COMBO_NF
            if checklist_combo.name == checklist:
                return Pass()
            else:
                return Fail("Selected checklist (%s) doesn't match the "
                            "required one (%s)"
                            % (checklist_combo.name, checklist))
        elif mode == "random":
            return Pass()
        else:
            return Fail("Unknown mode: %s" % mode)

@handle_act('/select_checklist')
def checklist_handler(element, app_node, local_node):
    return checklist_manipulate(element, app_node, local_node, False)

@handle_chck('/select_checklist')
@check_action_result
def checklist_check(element, app_node, local_node):
    return checklist_manipulate(element, app_node, local_node, True)

@handle_act('/changes')
def changes_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/changes')
def changes_check(element, app_node, local_node):
    return Pass()

@handle_act('/changes/info')
@handle_act('/changes/warning')
@handle_act('/changes/error')
def changes_line_handler(element, app_node, local_node):
    # TODO: implement separate info/warning/error handlers when/if it becomes
    # possible to recognize the different message types through ATK
    if element in {'/changes/info', '/changes/warning', '/changes/error'}:
        logger.warn("Specialized handler for %s not available, using "
                    "generic one.", element)

CHANGES_LABEL_NF = NotFound("\"Changes that were done...\" label",
                            "label_not_found")
CHANGES_PANE_NF = NotFound("scroll pane", fail_type="pane_not_found",
                           whose="table with changes")
CHANGES_TABLE_NF = NotFound("table with changes", "table_not_found")
CHANGES_TABLE_LINE_NF = NotFound("line \"%s\"", "cell_not_found",
                                 where="changes table")
@handle_chck('/changes/info')
@handle_chck('/changes/warning')
@handle_chck('/changes/error')
def changes_line_check(element, app_node, local_node):
    raw_text = get_attr(element, "text")
    params = get_attr(element, "params")
    if params is not None:
        params = tuple(params.split())
    # ugly workaround for broken translations:
    if raw_text in ("No rules for the pre-installation phase",
                    "make sure to create password with minimal length of %d characters"):
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
        return CHANGES_LABEL_NF
    try:
        changes_pane = getsibling(changes_label, 1, "scroll pane")
    except TimeoutError:
        return CHANGES_PANE_NF
    try:
        changes_table = getnode(changes_pane, "table")
    except TimeoutError:
        return CHANGES_TABLE_NF
    try:
        getnode_scroll(changes_table, "table cell", translated_text)
        return True
    except TimeoutError:
        return CHANGES_TABLE_LINE_NF % translated_text

DONE_BUTTON_NF = NotFound("\"Done\" button", "button_not_found")
@handle_act('/done')
@handle_act('/change_content/done')
def done_handler(element, app_node, local_node):
    try:
        done_button = getnode(local_node, "push button", tr("_Done", False))
    except TimeoutError:
        return DONE_BUTTON_NF
    done_button.click()

@handle_chck('/done')
@handle_chck('/change_content/done')
@check_action_result
def done_check(element, app_node, local_node):
    try:
        getnode_scroll(app_node, "spoke selector", oscap_tr("SECURITY POLICY"))
    except TimeoutError:
        return SPOKE_SELECTOR_NF
    return Pass()

