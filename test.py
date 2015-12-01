#!/bin/env python2

import libxml2, sys

from functions import waiton, screenshot

ACTIONS = {}

def handle_action(e_type, name):
    def tmp(func):
        ACTIONS[(e_type, name)] = func
        return func
    return tmp

def handle_step(element, node):
    ACTIONS.get((element.type, element.name),
                ACTIONS[(None, None)])(element, node)

@handle_action('text', 'text')
@handle_action('comment', 'comment')
def noop_handler(element, node):
    pass

@handle_action(None, None)
def default_handler(element, node):
#    print 'Unhandled element: %s' % element.name
    child = element.children
    while child is not None:
        handle_step(child, node)
        child = child.next

#@handle_action('element', 'installation')
#def installation_handler(element, node):
#    child = element.children
#    while child is not None:
#        handle_step(child, node)
#        child = child.next    

@handle_action('element', 'welcome')
def welcome_handler(element, node):
    default_handler(element, node)
    welcome = waiton(node, GenericPredicate(roleName="panel", name="WELCOME"))
    print 'CLICKING CONTINUE'
    welcome.child(roleName="push button", name="_Continue").click()

@handle_action('element', 'language')
def welcome_language_handler(element, node):
    lang = str(element.properties.content)
    gui_lang_search = waiton(node, GenericPredicate(roleName="text"))
    gui_lang_search.typeText(lang)
    gui_lang = waiton(node, GenericPredicate(roleName="table cell", name=lang))
    gui_lang.click()

if __name__ == "__main__":
    import os
    os.environ["DISPLAY"] = ":1"

    import dogtail.utils
    dogtail.utils.enableA11y()
    from dogtail.predicate import GenericPredicate
    import dogtail.tree
    anaconda = dogtail.tree.root.child(roleName="application", name="anaconda")

    doc = libxml2.parseFile("examples/autostep.xml")
    handle_step(doc, anaconda)
    doc.freeDoc()
