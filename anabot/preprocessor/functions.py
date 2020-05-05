import logging

logger = logging.getLogger('anabot.preprocessor')

import libxml2
import os

def tag_elements(elem, value, name="_replacing"):
    tag_element(elem, value, name)
    for child in elem.xpathEval("./*"):
        tag_elements(child, value, name)

def tag_element(elem, value, name="_replacing"):
    elem.setProp(name, value)

def load_snippet(name, original_element=None, copy_attrs=False,
                 tag_name="_replacing"):
    tdoc = libxml2.parseFile(os.path.dirname(__file__) +
                             '/snippets' + name + ".xml")
    doc = tdoc.copyDoc(True) # cannot modify document unless it's copied
    new = doc.getRootElement()
    if copy_attrs:
        for prop in original_element.xpathEval("./@*"):
            new.addChild(prop.copyProp(None))
    if original_element is not None:
        tag_elements(new, original_element.nodePath(), tag_name)
    tdoc.freeDoc()
    return new

def has_property(element, prop_name, namespace=None):
    return element.hasNsProp(prop_name, namespace) is not None

def pop_property(element, prop_name, namespace=None):
    prop = element.xpathEval('./@' + prop_name)
    if len(prop) != 1:
        return
    prop = prop[0].copyNode(True)
    element.unsetProp(prop_name)
    return prop

def pop_child(element, child_name):
    pass

def copy_content(src, dst, prepend=False):
    for prop in src.xpathEval("./@*"):
        dst.addChild(prop)
    if prepend:
        try:
            first_el = dst.xpathEval("./*")[0]
        except IndexError:
            first_el = None
        for child in src.xpathEval("./*"):
            dst.addChild(child)
            if first_el is not None:
                first_el.addPrevSibling(child)
    else:
        for child in src.xpathEval("./*"):
            dst.addChild(child)
