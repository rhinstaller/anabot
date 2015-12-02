#!/bin/env python2

import libxml2, sys
import time

from functions import waiton, waiton_all, screenshot, TimeoutError, get_attr

ACTIONS = {}

def handle_action(element_path):
    def tmp(func):
        ACTIONS[element_path] = func
        return func
    return tmp

def handle_step(element, node):
    ACTIONS.get(element.nodePath(), ACTIONS[None])(element, node)

def default_handler(element, node):
    for child in element.xpathEval("./*"):
        handle_step(child, node)

@handle_action(None)
def unimplemented_handler(element, node):
    print 'Unhandled element: %s' % element.name
    default_handler(element, node)

@handle_action('/installation')
def installation_handler(element, node):
    default_handler(element, node)

@handle_action('/installation/welcome')
def welcome_handler(element, node):
    default_handler(element, node)
    welcome = waiton(node, GenericPredicate(roleName="panel", name="WELCOME"))
    print 'CLICKING CONTINUE'
    welcome.child(roleName="push button", name="_Continue").click()

@handle_action('/installation/welcome/language')
def welcome_language_handler(element, node):
    lang = get_attr(element, "value")
    gui_lang_search = waiton(node, GenericPredicate(roleName="text"))
    gui_lang_search.typeText(lang)
    time.sleep(1)
    gui_lang = waiton(node, GenericPredicate(roleName="table cell", name=lang))
    gui_lang.click()

@handle_action('/installation/welcome/locality')
def welcome_language_handler(element, node):
    locality = get_attr(element, "value")
    gui_locality = waiton(node,
                          GenericPredicate(roleName="table cell",
                                           name=".* (%s)" % locality))
    gui_locality_first = waiton(node,
                                GenericPredicate(roleName="table cell",
                                                 name=".* (.*)"))
    gui_locality_first.click()
    time.sleep(1)
    while not gui_locality.selected:
        gui_locality_first.parent.keyCombo("Down")
        time.sleep(1)

@handle_action('/installation/hub')
def hub_handler(element, node):
    default_handler(element, node)
    begin_button = waiton(node,
                          GenericPredicate(roleName="push button",
                                           name="Begin Installation"))
    begin_button.click()

@handle_action('/installation/hub/partitioning')
def hub_partitioning_handler(element, node):
    partitioning_spoke = waiton(node,
                                GenericPredicate(roleName="spoke selector",
                                                 name="INSTALLATION DESTINATION"))
    partitioning_spoke.click()
    default_handler(element, node)

@handle_action('/installation/hub/partitioning/disk')
def hub_partitioning_handler_disk(element, node):
    name = get_attr(element, "name")
    action = get_attr(element, "action", "select")
    disks = waiton_all(node,
                       GenericPredicate(roleName="disk overview"))
    if name != "*":
        disks = [ disk for disk in disks if disk.children[0].children[3].text == name ]
    for disk in disks:
        if action == "select" and True:
            disk.click()
        elif action == "deselect" and True:
            disk.click()

@handle_action('/installation/hub/partitioning/mode')
def hub_partitioning_handler_additional_space(element, node):
    mode = get_attr(element, "mode")
    if mode == "default":
        return
    if mode == "automatic":
        radio = waiton(node,
                       GenericPredicate(roleName="radio button",
                                        name="Automatically configure partitioning."))
    if mode == "manual":
        radio = waiton(node,
                       GenericPredicate(roleName="radio button",
                                        name="I will configure partitioning."))
    if not radio.checked:
        radio.click()

@handle_action('/installation/hub/partitioning/additional_space')
def hub_partitioning_handler_additional_space(element, node):
    action = get_attr(element, "action", "enable")
    additional_checkbox = waiton(node,
                                 GenericPredicate(roleName="check box",
                                                  name="I would like to make additional space available."))
    if (action == "enable") != additional_checkbox.checked:
        additional_checkbox.click()

@handle_action('/installation/hub/partitioning/done')
def hub_partitioning_handler_done(element, node):
    destination_panel = waiton(node,
                               GenericPredicate(roleName="panel",
                                                name="INSTALLATION DESTINATION"))
    done_button = waiton(destination_panel,
                         GenericPredicate(roleName="push button",
                                          name="_Done"))
    done_button.click()

@handle_action('/installation/hub/partitioning/reclaim')
def hub_partitioning_handler_reclaim(element, node):
    # TODO action=reclaim/cancel
    default_handler(element, node)
    reclaim_button = waiton(node, GenericPredicate(roleName="push button",
                                                   name="Reclaim space"))
    reclaim_button.click()

@handle_action('/installation/hub/partitioning/reclaim/delete_all')
def hub_partitioning_handler_reclaim_delete_all(element, node):
    delete_all_button = waiton(node, GenericPredicate(roleName="push button",
                                                      name="Delete all"))
    delete_all_button.click()

@handle_action('/installation/configuration')
def hub_configuration_handler(element, node):
    default_handler(element, node)
    print "WAITING FOR REBOOT"
    reboot_button = waiton(node, GenericPredicate(roleName="push button",
                                                  name="Reboot"),
                           timeout=float("inf"))
    reboot_button.click()    

@handle_action('/installation/configuration/root_password')
def configuration_root_password_handler(element, node):
    root_password_spoke = waiton(node,
                                 GenericPredicate(roleName="spoke selector",
                                                  name="ROOT PASSWORD"))
    root_password_spoke.click()
    default_handler(element, node)
    root_password_panel = waiton(node,
                                 GenericPredicate(roleName="panel",
                                                  name="ROOT PASSWORD"))
    root_password_done = waiton(root_password_panel,
                                GenericPredicate(roleName="push button",
                                                 name="_Done"))
    root_password_done.click()

@handle_action('/installation/configuration/root_password/password')
def configuration_root_password_handler(element, node):
    value = get_attr(element, "value")
    password_entry = waiton(node,
                            GenericPredicate(roleName="password text",
                                             name="Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_action('/installation/configuration/root_password/confirm_password')
def configuration_root_password_handler(element, node):
    value = get_attr(element, "value")
    password_entry = waiton(node,
                            GenericPredicate(roleName="password text",
                                             name="Confirm Password"))
    password_entry.click()
    password_entry.typeText(value)

if __name__ == "__main__":
    import os
    os.environ["DISPLAY"] = ":1"

    import dogtail.utils
    dogtail.utils.enableA11y()
    import dogtail.config
    dogtail.config.config.typingDelay = 1
    from dogtail.predicate import GenericPredicate
    import dogtail.tree
    anaconda = dogtail.tree.root.child(roleName="application", name="anaconda")

    doc = libxml2.parseFile("examples/autostep.xml")
    handle_step(doc.getRootElement(), anaconda)
    doc.freeDoc()
