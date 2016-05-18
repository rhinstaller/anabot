import logging
logger = logging.getLogger('anabot')

from random import randint
import gettext

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getnodes, getsibling, getparents
from anabot.runtime.translate import tr

_local_path = '/installation/hub/oscap_addon'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
_tr = lambda x: str(gettext.ldgettext("oscap-anaconda-addon", x))

@handle_act('')
def base_handler(element, app_node, local_node):
    oscap_addon = getnode(app_node, "spoke selector",
                          _tr("SECURITY POLICY"))
    oscap_addon.click()
    oscap_addon_label = getnode(app_node, "label", _tr("SECURITY POLICY"))
    oscap_addon_panel = getparents(oscap_addon_label, predicates={'roleName': 'panel'})[2]
    default_handler(element, app_node, oscap_addon_panel)

@handle_act('/choose')
def choose_handler(element, app_node, local_node):
    mode = get_attr(element, "mode", "manual")
    profiles_label = getnode(local_node, "label", _tr("Choose profile below:"))
    profiles_table = getsibling(profiles_label, 2)
    available_profiles = [p for p in getnodes(profiles_table, "table cell")
                          if p.text]
    profile = None # profile to be selected
    if mode == "manual":
        profile_name = get_attr(element, "profile")
        profile = [p for p in available_profiles
                   if p.name.splitlines()[0] == profile_name][0]
    elif mode == "random":
        profile = available_profiles[randint(0, len(available_profiles) - 1)]
    # choose a random profile other than already selected
    elif mode == "random_strict":
        if len(available_profiles) > 1:
            selected_profile = [p for p in available_profiles
                                if p.selected and p.text]
            if len(selected_profile) == 0:
                profile = available_profiles[randint(0, len(available_profiles) - 1)]
            elif len(selected_profile) == 1:
                profile_no = available_profiles.index(selected_profile[0])
                while profile == None or profile_no == available_profiles.index(profile):
                    profile = available_profiles[randint(0, len(available_profiles) - 1)]
        else:
            profile = available_profiles[0]
    else:
        logger.warning("Unknown selection mode: %s" % mode)
        return
    profile.click()

@handle_act('/select')
def select_handler(element, app_node, local_node):
    select_button = getnode(local_node, "push button", _tr("Select profile"))
    select_button.click()

@handle_act('/change_content')
def change_content_handler(element, app_node, local_node):
    change_button = getnode(local_node, "push button", _tr("Change content"))
    change_button.click()
    default_handler(element, app_node, local_node)

@handle_act('/change_content/source')
def change_content_source_handler(element, app_node, local_node):
    fetch_button = getnode(app_node, "push button", _tr("Fetch"))
    datastream_url_input = getsibling(fetch_button, -2)
    url = get_attr(element, "url")
    datastream_url_input.typeText(url)

@handle_act('/change_content/fetch')
def change_content_fetch_handler(element, app_node, local_node):
    fetch_button = getnode(app_node, "push button", _tr("Fetch"))
    fetch_button.click()

@handle_act('/change_content/use_ssg')
def change_content_use_ssg_handler(element, app_node, local_node):
    use_ssg_button = getnode(local_node, "push button", _tr("Use SCAP Security Guide"))
    use_ssg_button.click()

@handle_act('/apply_policy')
def apply_policy_handler(element, app_node, local_node):
    policy_action = get_attr(element, "action")
    apply_policy_label = getnode(local_node, "label", _tr("Apply security policy:"))
    policy_button = getsibling(apply_policy_label, 2)
    policy_button.click()
    if (policy_action == "enable" and not policy_button.checked
        or policy_action == "disable" and policy_button.checked):
        policy_button.click()

@handle_act('/select_datastream')
def datastream_handler(element, app_node, local_node):
    datastream = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    ds_label = getnode(local_node, "label", _tr("Data stream:"))
    ds_combo = getsibling(ds_label, 2)
    ds_combo.click()
    ds_items = getnodes(ds_combo, "menu item")
    if mode == "manual":
        ds_item = getnode(ds_combo, "menu item", datastream)
    elif mode == "random":
        ds_item = ds_items[randint(0, len(ds_items)-1)]
    ds_item.click()

@handle_act('/select_checklist')
def checklist_handler(element, app_node, local_node):
    checklist = get_attr(element, "id")
    mode = get_attr(element, "mode", "manual")
    checklist_label = getnode(local_node, "label", _tr("Checklist:"))
    checklist_combo = getsibling(checklist_label, 2)
    checklist_combo.click()
    checklist_items = getnodes(checklist_combo, "menu item")
    if mode == "manual":
        checklist_item = getnode(checklist_combo, "menu item", checklist)
    elif mode == "random":
        checklist_item = checklist_items[randint(0, len(checklist_items)-1)]
    checklist_item.click()

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()
