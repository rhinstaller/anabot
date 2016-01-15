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

def has_property(element, prop_name):
    return len(element.xpathEval("./@" + prop_name)) == 1

def pop_property(element, prop_name):
    prop = element.xpathEval("./@" + prop_name)
    if prop is None:
        return
    prop = prop[0].copyNode(True)
    element.unsetProp(prop_name)
    return prop

def pop_child(element, child_name):
    pass

