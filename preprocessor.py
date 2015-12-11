#!/bin/env python

import libxml2
import sys, re

REPLACES = {}
DEFAULTS = {}

def replace(node_path):
    def decorator(func):
        REPLACES[node_path] = func
        return func
    return decorator

def default(node_path):
    def decorator(func):
        DEFAULTS[node_path] = func
        return func
    return decorator

def pop_property(element, prop_name):
    pass

def tag_element(new, orig, tag_name="_replacing"):
    new.newProp(tag_name, orig.nodePath())

def pop_child(element, child_name):
    pass

@replace(None)
def copy(element):
    new = element.copyNode(False)
    for prop in element.xpathEval("./@*"):
        new.addChild(prop.copyProp(None))
    return new

@replace("/installation/welcome")
def replace_welcome(original):
    lang_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")
    new = original.copyNode(False)
    for prop in original.xpathEval("./@*"):
        if prop.name == "language":
            tag_element(new, original)
            match = lang_re.match(prop.content)

            lang = match.group("lang")
            lang_el = new.newChild(None, "language", "")
            lang_el.newProp("value", lang)
            tag_element(lang_el, original)

            loc = match.group("loc")
            loc_el = new.newChild(None, "locality", "")
            loc_el.newProp("value", loc)
            tag_element(loc_el, original)
        else:
            new.addChild(prop.copyProp(None))
    return new

def copy_replace_tree(src_element, dst_parent, root=False):
    child = src_element.children
    while child is not None:
        if child.type == "element" and child.nodePath() in REPLACES:
            new_child = REPLACES[child.nodePath()](child)
        else:
            new_child = REPLACES[None](child)
        if root:
            dst_parent.setRootElement(new_child)
        else:
            dst_parent.addChild(new_child)
        copy_replace_tree(child, new_child)
        child = child.next

def preprocess(input_path, output_path):
    indoc = libxml2.parseFile(input_path)
    outdoc = indoc.copyDoc(False)
    copy_replace_tree(indoc, outdoc, True)
    indoc.dump(open(output_path + '.orig', 'w'))
    outdoc.dump(open(output_path, 'w'))
    print outdoc.serialize(format=1)
    indoc.freeDoc()
    outdoc.freeDoc()

if __name__ == "__main__":
    sys.exit(preprocess(*sys.argv[1:]))
