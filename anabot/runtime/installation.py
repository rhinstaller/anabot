import logging
logger = logging.getLogger('anabot')

import time
from fnmatch import fnmatchcase

from .decorators import handle_action, handle_check
from .default import default_handler
from .functions import get_attr, getnode, getnodes, getselected
from .errors import TimeoutError
from .translate import set_languages_by_name, tr

@handle_action('/installation')
def installation_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_action('/installation/welcome')
def welcome_handler(element, app_node, local_node):
    welcome = getnode(app_node, "panel", "WELCOME")
    default_handler(element, app_node, welcome)
    locales = getnode(welcome, "table", "Locales")
    set_languages_by_name(getselected(locales)[0].name)
    getnode(welcome, "push button", "_Continue").click()

@handle_action('/installation/welcome/language')
def welcome_language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang_search = getnode(local_node, node_type="text")
    gui_lang_search.typeText(lang)
    gui_lang = getnode(local_node, "table cell", lang)
    gui_lang.click()

@handle_check('/installation/welcome/language')
def welcome_language_check(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang = getnode(local_node, "table cell", lang)
    return gui_lang.selected

@handle_action('/installation/welcome/locality')
def welcome_locality_handler(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell", ".* (%s)" % locality)
    gui_locality_first = getnode(local_node, "table cell", ".* (.*)")
    gui_locality_first.click()
    time.sleep(1)
    while not gui_locality.selected:
        gui_locality_first.parent.keyCombo("Down")
        time.sleep(1)

@handle_check('/installation/welcome/locality')
def welcome_locality_check(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell",
                           ".* ({0})".format(locality))
    return gui_locality.selected

@handle_action('/installation/hub')
def hub_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    begin_button = getnode(app_node, "push button",
                           tr("_Begin Installation", context="GUI|Summary"))
    begin_button.click()

@handle_action('/installation/hub/partitioning')
def hub_partitioning_handler(element, app_node, local_node):
    partitioning = getnode(app_node, "spoke selector",
                           tr("INSTALLATION DESTINATION"))
    partitioning.click()
    partitioning_panel = getnode(app_node, "panel",
                                 tr("INSTALLATION DESTINATION"))
    default_handler(element, app_node, partitioning_panel)

@handle_action('/installation/hub/partitioning/disk')
def hub_partitioning_handler_disk(element, app_node, local_node):
    name = get_attr(element, "name")
    action = get_attr(element, "action", "select")
    disks = getnodes(local_node, node_type="disk overview")
    disks = [disk for disk in disks
             if fnmatchcase(disk.children[0].children[3].text, name)]
    for disk in disks:
        # selected disk has icon without name
        icon = getnode(disk, node_type="icon")
        if action == "select" and not disk.name != "":
            disk.click()
        elif action == "deselect" and icon.name == "":
            disk.click()

@handle_action('/installation/hub/partitioning/mode')
def hub_partitioning_handler_mode(element, app_node, local_node):
    mode = get_attr(element, "mode")
    if mode == "default":
        return
    if mode == "automatic":
        radio_text = tr("A_utomatically configure partitioning.")
    if mode == "manual":
        radio_text = tr("_I will configure partitioning.")
    radio = getnode(local_node, "radio button", radio_text)
    if not radio.checked:
        radio.click()

@handle_action('/installation/hub/partitioning/additional_space')
def hub_partitioning_handler_additional_space(element, app_node, local_node):
    action = get_attr(element, "action", "enable")
    checkbox_text = tr("I would like to _make additional space available.")
    additional_checkbox = getnode(local_node, "check box", checkbox_text)
    if (action == "enable") != additional_checkbox.checked:
        additional_checkbox.click()

@handle_action('/installation/hub/partitioning/done')
def hub_partitioning_handler_done(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()

@handle_action('/installation/hub/partitioning/reclaim')
def hub_partitioning_handler_reclaim(element, app_node, local_node):
    # TODO action=reclaim/cancel
    reclaim_dialog = None
    for dialog in getnodes(app_node, "dialog"):
        try:
            getnode(dialog, "label", tr("RECLAIM DISK SPACE"))
            reclaim_dialog = dialog
        except TimeoutError:
            pass
    if reclaim_dialog is None:
        return (False, "Reclaim dialog not found")
    default_handler(element, app_node, reclaim_dialog)
    reclaim_button = getnode(reclaim_dialog, "push button",
                             tr("_Reclaim space", context="GUI|Reclaim Dialog"))
    reclaim_button.click()

@handle_action('/installation/hub/partitioning/reclaim/delete_all')
def hub_partitioning_handler_reclaim_delete_all(element, app_node, local_node):
    delete_all_button = getnode(local_node, "push button",
                                tr("Delete _all", context="GUI|Reclaim Dialog"))
    delete_all_button.click()

@handle_action('/installation/configuration')
def hub_configuration_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    logger.debug("WAITING FOR REBOOT")
    reboot_button = getnode(app_node, "push button",
                            tr("_Reboot", context="GUI|Progress"),
                            timeout=float("inf"))
    reboot_button.click()

@handle_action('/installation/configuration/root_password')
def configuration_root_password_handler(element, app_node, local_node):
    root_password_spoke = getnode(app_node, "spoke selector",
                                  tr("_ROOT PASSWORD", context="GUI|Spoke"))
    root_password_spoke.click()
    try:
        root_password_panel = getnode(app_node, "panel", tr("ROOT PASSWORD"))
    except TimeoutError:
        return (False, "Root password spoke not found")
    default_handler(element, app_node, root_password_panel)

@handle_action('/installation/configuration/root_password/password')
def configuration_root_password_text_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text", tr("Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_action('/installation/configuration/root_password/confirm_password')
def configuration_root_password_confirm_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text",
                             tr("Confirm Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_action('/installation/configuration/root_password/done')
def configuration_root_password_done_handler(element, app_node, local_node):
    try:
        root_password_done = getnode(local_node, "push button",
                                     tr("_Done", False))
    except TimeoutError:
        return (False, "Done button not found or not clickable")

    root_password_done.click()
    return True # done for password found and was clicked
