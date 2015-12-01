#!/bin/env python2

import libxml2, sys
import time

from functions import waiton, screenshot, TimeoutError

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

@handle_action('text')
@handle_action('comment')
def noop_handler(element, node):
    pass

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
    lang = str(element.properties.content)
    gui_lang_search = waiton(node, GenericPredicate(roleName="text"))
    gui_lang_search.typeText(lang)
    time.sleep(1)
    gui_lang = waiton(node, GenericPredicate(roleName="table cell", name=lang))
    gui_lang.click()

@handle_action('/installation/welcome/locality')
def welcome_language_handler(element, node):
    pass

if __name__ == "__main__":
    import os
    os.environ["DISPLAY"] = ":1"

    import dogtail.utils
    dogtail.utils.enableA11y()
    from dogtail.predicate import GenericPredicate
    import dogtail.tree
    anaconda = dogtail.tree.root.child(roleName="application", name="anaconda")

    doc = libxml2.parseFile("examples/autostep.xml")
    handle_step(doc.getRootElement(), anaconda)
    doc.freeDoc()
