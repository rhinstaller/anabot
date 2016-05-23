import logging
logger = logging.getLogger('anabot')

from random import randint
import gettext

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getnodes, getsibling
from anabot.runtime.functions import getparents, TimeoutError
from anabot.runtime.translate import tr

_local_path = '/installation/hub/oscap_addon'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
_tr = lambda x: str(gettext.ldgettext("oscap-anaconda-addon", x))
_chosen_profile = None
_selected_profile = None
_oscap_addon_visited = False
_change_content_visited = False

@handle_act('')
def base_handler(element, app_node, local_node):
    global _oscap_addon_visited
    _oscap_addon_visited = False
    oscap_addon = getnode(app_node, "spoke selector", _tr("SECURITY POLICY"))
    oscap_addon.click()
    oscap_addon_label = getnode(app_node, "label", _tr("SECURITY POLICY"))
    oscap_addon_panel = getparents(oscap_addon_label, predicates={'roleName': 'panel'})[2]
    _oscap_addon_visited = True
    default_handler(element, app_node, oscap_addon_panel)

@handle_chck('')
def base_check(element, app_node, local_node):
    return _oscap_addon_visited

def choose_manipulate(element, app_node, local_node, dryrun):
    mode = get_attr(element, "mode", "manual")
    profiles_label = getnode(local_node, "label", _tr("Choose profile below:"))
    profiles_table = getsibling(profiles_label, 2)
    available_profiles = [p for p in getnodes(profiles_table, "table cell")
                          if p.text]
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
            return
    elif mode == "random":
        profile = available_profiles[randint(0, len(available_profiles) - 1)]
    # choose a random profile other than already selected
    elif mode == "random_strict":
        if len(available_profiles) > 1:
            if len(selected_profile) == 0:
                profile = available_profiles[randint(0, len(available_profiles) - 1)]
            elif len(selected_profile) == 1:
                profile_no = available_profiles.index(selected_profile[0])
                while profile == None or profile_no == available_profiles.index(profile):
                    profile = available_profiles[randint(0, len(available_profiles) - 1)]
        else:
            profile = available_profiles[0]
    else:
        if dryrun:
            return False
        else:
            logger.warning("Unknown selection mode: %s" % mode)
            return

    if dryrun:
        selected = lambda x: x.selected
        if mode == "manual":
            result = profile.selected
        elif mode == "random":
            result = any(map(selected, available_profiles))
        elif mode == "random_strict":
            result = any(map(selected, [p for p in available_profiles
                                        if p is not _chosen_profile]))
        else:
            result = False
        return result
    else:
        global _selected_profile
        _selected_profile = profile
        profile.click()

@handle_act('/choose')
def choose_handler(element, app_node, local_node):
    choose_manipulate(element, app_node, local_node, False)

@handle_chck('/choose')
def choose_check(element, app_node, local_node):
    return choose_manipulate(element, app_node, local_node, True)

@handle_act('/select')
def select_handler(element, app_node, local_node):
    select_button = getnode(local_node, "push button", _tr("Select profile"), sensitive=None)
    select_button.click()

@handle_chck('/select')
def select_check(element, app_node, local_node):
    select_button = getnode(local_node, "push button", _tr("Select profile"), sensitive=False)
    if _selected_profile is None or select_button.sensitive:
        result = False
    else:
        result = _selected_profile.selected and not select_button.sensitive
    return result

@handle_act('/change_content')
def change_content_handler(element, app_node, local_node):
    change_button = getnode(local_node, "push button", _tr("Change content"))
    change_button.click()
    global _change_content_visited
    try:
        getnode(local_node, "push button", _tr("Use SCAP Security Guide"))
        _change_content_visited = True
    except TimeoutError:
        _change_content_visited = False
    default_handler(element, app_node, local_node)

@handle_chck('/change_content')
def change_content_check(element, app_node, local_node):
    return _change_content_visited

@handle_act('/change_content/source')
def change_content_source_handler(element, app_node, local_node):
    fetch_button = getnode(local_node, "push button", _tr("Fetch"))
    datastream_url_input = getsibling(fetch_button, -2)
    url = get_attr(element, "url")
    datastream_url_input.typeText(url)

@handle_chck('/change_content/source')
def change_content_source_check(element, app_node, local_node):
    fetch_button = getnode(local_node, "push button", _tr("Fetch"))
    datastream_url_input = getsibling(fetch_button, -2)
    url = get_attr(element, "url")
    return datastream_url_input.text == url

@handle_act('/change_content/fetch')
def change_content_fetch_handler(element, app_node, local_node):
    fetch_button = getnode(app_node, "push button", _tr("Fetch"))
    fetch_button.click()

@handle_chck('/change_content/fetch')
def change_content_fetch_check(element, app_node, local_node):
    try:
        infobar = getnode(local_node, "info bar",
                          predicates={"name": str(tr("Error"))})
        error = getnode(infobar, "label").text
        logger.info("SCAP content fetch error: \"%s\"" % error)
        result = False
    except TimeoutError:
        result = True
    return result

@handle_act('/change_content/use_ssg')
def change_content_use_ssg_handler(element, app_node, local_node):
    use_ssg_button = getnode(local_node, "push button", _tr("Use SCAP Security Guide"))
    use_ssg_button.click()

@handle_chck('/change_content/use_ssg')
def change_content_use_ssg_check(element, app_node, local_node):
    try:
        getnode(local_node, "push button", _tr("Use SCAP Security Guide"), visible=False)
        result = True
    except TimeoutError:
        result = False
    return result

@handle_act('/apply_policy')
def apply_policy_handler(element, app_node, local_node):
    policy_action = get_attr(element, "action")
    apply_policy_label = getnode(local_node, "label", _tr("Apply security policy:"))
    policy_button = getsibling(apply_policy_label, 2)
    policy_button.click()
    if (policy_action == "enable" and not policy_button.checked
        or policy_action == "disable" and policy_button.checked):
        policy_button.click()

@handle_chck('/apply_policy')
def apply_policy_check(element, app_node, local_node):
    policy_action = get_attr(element, "action")
    apply_policy_label = getnode(local_node, "label", _tr("Apply security policy:"))
    policy_button = getsibling(apply_policy_label, 2)
    return  (policy_action == "enable" and policy_button.checked
             or policy_action == "disable" and not policy_button.checked)

@handle_act('/select_datastream')
def datastream_handler(element, app_node, local_node):
    datastream = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    ds_label = getnode(local_node, "label", _tr("Data stream:"))
    ds_combo = getsibling(ds_label, 2)
    ds_combo.click()
    ds_items = getnodes(ds_combo, "menu item")
    if mode == "manual":
        try:
            ds_item = getnode(ds_combo, "menu item", datastream)
        except TimeoutError:
            logger.info("Data stream '%s' not found" % datastream)
            ds_combo.click()
            return
    elif mode == "random":
        ds_item = ds_items[randint(0, len(ds_items)-1)]
    ds_item.click()

@handle_chck('/select_datastream')
def datastream_chck(element, app_node, local_node):
    result = False
    mode = get_attr(element, "mode", "manual")
    if mode == "random":
        result = True
    elif mode == "manual":
        datastream = get_attr(element, "id")
        ds_label = getnode(local_node, "label", _tr("Data stream:"))
        ds_combo = getsibling(ds_label, 2)
        result = ds_combo.name == datastream
    return result

@handle_act('/select_checklist')
def checklist_handler(element, app_node, local_node):
    checklist = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    checklist_label = getnode(local_node, "label", _tr("Checklist:"))
    checklist_combo = getsibling(checklist_label, 2)
    checklist_combo.click()
    checklist_items = getnodes(checklist_combo, "menu item")
    if mode == "manual":
        try:
            checklist_item = getnode(checklist_combo, "menu item", checklist)
        except TimeoutError:
            logger.info("Checklist '%s' not found" % checklist)
            checklist_combo.click()
            return
    elif mode == "random":
        checklist_item = checklist_items[randint(0, len(checklist_items)-1)]
    checklist_item.click()

@handle_chck('/select_checklist')
def checklist_check(element, app_node, local_node):
    result = False
    mode = get_attr(element, "mode", "manual")
    if mode == "random":
        result = True
    elif mode == "manual":
        datastream = get_attr(element, "id")
        checklist_label = getnode(local_node, "label", _tr("Checklist:"))
        checklist_combo = getsibling(checklist_label, 2)
        result = checklist_combo.name == datastream
    return result

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()

@handle_chck('/done')
def done_check(element, app_node, local_node):
    result = False
    try:
        oscap_addon_selector = getnode(app_node, "spoke selector",
                                       _tr("SECURITY POLICY"))
        oscap_addon_status = str(getnode(oscap_addon_selector, "label").text)
        if oscap_addon_status == _tr("Everything okay"):
            result = True
        else:
            logger.info("OSCAP addon status: \"%s\"" % oscap_addon_status)
    except TimeoutError:
        pass
    return result

