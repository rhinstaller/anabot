from ..variables import get_variables

from . import EASY_NS_URI

def sub_element(element):
    #help(element)
    name = element.nsProp("name", EASY_NS_URI)
    element.setName(name)
    element.unsetNsProp(element.ns(), "name")
    for attribute in element.xpathEval("@*"):
        attribute.setContent(attribute.content.format(**get_variables()))
