import logging

logger = logging.getLogger('anabot.preprocessor')

from .decorators import replace

@replace(None)
def copy(element):
    new = element.copyNode(False)
    for prop in element.xpathEval("./@*"):
        new.addChild(prop.copyProp(None))
    return new
