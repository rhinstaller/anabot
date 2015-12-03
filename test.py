#!/bin/env python2

import libxml2, sys
import time, re

from fnmatch import fnmatchcase

from functions import waiton, waiton_all, screenshot, TimeoutError, get_attr, getnode, getnodes

ACTIONS = {}
CHECKS = {}
NODE_NUM = re.compile(r'\[[0-9]+\]')

def handle_action(element_path):
    def tmp(func):
        ACTIONS[element_path] = func
        return func
    return tmp

def handle_check(element_path):
    def tmp(func):
        CHECKS[element_path] = func
        return func
    return tmp

def handle_step(element, app_node, local_node):
    node_path = re.sub(NODE_NUM, '', element.nodePath())
    policy = get_attr(element, "policy", "should_pass")
    handler_path = node_path
    if handler_path not in ACTIONS:
        handler_path = None
    if policy in ("should_pass", "should_fail", "may_fail"):
        ACTIONS.get(handler_path)(element, app_node, local_node)
    if handler_path is None:
        return
    if handler_path not in CHECKS:
        handler_path = None
    if policy in ("should_pass", "just_check"):
        # ASSERT
        CHECKS.get(handler_path)(element, app_node, local_node)
    if policy in ("should_fail"):
        # NEGATIVE ASSERT
        CHECKS.get(handler_path)(element, app_node, local_node)

def default_handler(element, app_node, local_node):
    for child in element.xpathEval("./*"):
        handle_step(child, app_node, local_node)

@handle_action(None)
def unimplemented_handler(element, app_node, local_node):
    print 'Unhandled element: %s' % element.nodePath()
    default_handler(element, app_node, local_node)

@handle_check(None)
def unimplemented_handler_check(element, app_node, local_node):
    print 'Unhandled check for element: %s' % element.nodePath()

@handle_action('/installation')
def installation_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_action('/installation/welcome')
def welcome_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    welcome = getnode(app_node, "panel", "WELCOME")
    getnode(welcome, "push button", "_Continue").click()

@handle_action('/installation/welcome/language')
def welcome_language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    welcome = getnode(app_node, "panel", "WELCOME")
    gui_lang_search = getnode(welcome, node_type="text")
    gui_lang_search.typeText(lang)
    gui_lang = getnode(app_node, "table cell", lang)
    gui_lang.click()

@handle_action('/installation/welcome/locality')
def welcome_language_handler(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(app_node, "table cell", ".* (%s)" % locality)
    gui_locality_first = getnode(app_node, "table cell", ".* (.*)")
    gui_locality_first.click()
    time.sleep(1)
    while not gui_locality.selected:
        gui_locality_first.parent.keyCombo("Down")
        time.sleep(1)

@handle_action('/installation/hub')
def hub_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    begin_button = getnode(app_node, "push button", "Begin Installation")
    begin_button.click()

@handle_action('/installation/hub/partitioning')
def hub_partitioning_handler(element, app_node, local_node):
    partitioning = getnode(app_node, "spoke selector", "INSTALLATION DESTINATION")
    partitioning.click()
    default_handler(element, app_node, local_node)

@handle_action('/installation/hub/partitioning/disk')
def hub_partitioning_handler_disk(element, app_node, local_node):
    name = get_attr(element, "name")
    action = get_attr(element, "action", "select")
    disks = getnodes(app_node, node_type="disk overview")
    disks = [ disk for disk in disks if fnmatchcase(disk.children[0].children[3].text, name) ]
    for disk in disks:
        # selected disk has icon without name
        icon = getnode(disk, node_type="icon")
        if action == "select" and icon.name == "Hard Disk":
            disk.click()
        elif action == "deselect" and icon.name == "":
            disk.click()

@handle_action('/installation/hub/partitioning/mode')
def hub_partitioning_handler_additional_space(element, app_node, local_node):
    mode = get_attr(element, "mode")
    if mode == "default":
        return
    if mode == "automatic":
        radio_text = "Automatically configure partitioning."
    if mode == "manual":
        radio_text = "I will configure partitioning."
    radio = getnode(app_node, "radio button", radio_text)
    if not radio.checked:
        radio.click()

@handle_action('/installation/hub/partitioning/additional_space')
def hub_partitioning_handler_additional_space(element, app_node, local_node):
    action = get_attr(element, "action", "enable")
    additional_checkbox = getnode(app_node, "check box", "I would like to make additional space available.")
    if (action == "enable") != additional_checkbox.checked:
        additional_checkbox.click()

@handle_action('/installation/hub/partitioning/done')
def hub_partitioning_handler_done(element, app_node, local_node):
    destination_panel = getnode(app_node, "panel", "INSTALLATION DESTINATION")
    done_button = getnode(destination_panel, "push button", "_Done")
    done_button.click()

@handle_action('/installation/hub/partitioning/reclaim')
def hub_partitioning_handler_reclaim(element, app_node, local_node):
    # TODO action=reclaim/cancel
    default_handler(element, app_node, local_node)
    reclaim_button = getnode(app_node, "push button", "Reclaim space")
    reclaim_button.click()

@handle_action('/installation/hub/partitioning/reclaim/delete_all')
def hub_partitioning_handler_reclaim_delete_all(element, app_node, local_node):
    delete_all_button = getnode(app_node, "push button", "Delete all")
    delete_all_button.click()

@handle_action('/installation/configuration')
def hub_configuration_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    print "WAITING FOR REBOOT"
    reboot_button = getnode(app_node, "push button", "Reboot", timeout=float("inf"))
    reboot_button.click()

@handle_action('/installation/configuration/root_password')
def configuration_root_password_handler(element, app_node, local_node):
    root_password_spoke = getnode(app_node, "spoke selector", "ROOT PASSWORD")
    root_password_spoke.click()
    default_handler(element, app_node, local_node)
    root_password_panel = getnode(app_node, "panel", "ROOT PASSWORD")
    root_password_done = getnode(root_password_panel, "push button", "_Done")
    root_password_done.click()

@handle_action('/installation/configuration/root_password/password')
def configuration_root_password_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(app_node, "password text", "Password")
    password_entry.click()
    password_entry.typeText(value)

@handle_action('/installation/configuration/root_password/confirm_password')
def configuration_root_password_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(app_node, "password text", "Confirm Password")
    password_entry.click()
    password_entry.typeText(value)

if __name__ == "__main__":
    import os
    os.environ["DISPLAY"] = ":1"

    import dogtail.utils
    dogtail.utils.enableA11y()
    import dogtail.config
    dogtail.config.config.typingDelay = 0.2
    from dogtail.predicate import GenericPredicate
    import dogtail.tree
    anaconda = dogtail.tree.root.child(roleName="application", name="anaconda")

    doc = libxml2.parseFile("examples/autostep.xml")
    handle_step(doc.getRootElement(), anaconda, None)
    doc.freeDoc()
