from ..variables import get_variables

from . import EASY_NS_URIS

def sub_element(element):
    #help(element)
    for EASY_NS_URI in EASY_NS_URIS:
        name = element.nsProp("name", EASY_NS_URI)
        if name is not None:
            break
    element.setName(name)
    element.unsetNsProp(element.ns(), "name")
    for attribute in element.xpathEval("@*"):
        try:
            attribute.setContent(attribute.content.format(**get_variables()))
        except KeyError as e:
            raise Exception("Undefined variable for substitution in Anabot recipe: %s" % e.args[0])
