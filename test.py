#!/bin/env python2

import libxml2, sys

ACTIONS = {}

def handle_action(e_type, name):
    def tmp(func):
        ACTIONS[(e_type, name)] = func
        return func
    return tmp

def handle_step(element):
    ACTIONS.get((element.type, element.name),
                ACTIONS[(None, None)])(element)

@handle_action('text', 'text')
@handle_action('comment', 'comment')
def noop_handler(element):
    pass

@handle_action(None, None)
def default_handler(element):
    print 'Unhandled element: %s' % element.name
    child = element.children
    while child is not None:
        handle_step(child)
        child = child.next

if __name__ == "__main__":
    doc = libxml2.parseFile("examples/autostep.xml")
    child = doc.children
    while child is not None:
        handle_step(child)
        child = child.next
    doc.freeDoc()
