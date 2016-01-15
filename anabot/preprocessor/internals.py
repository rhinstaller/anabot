import logging

logger = logging.getLogger('anabot.preprocessor')

from .decorators import _REPLACES, _DEFAULTS
from .functions import tag_elements

def copy_replace_tree(src_element, dst_parent, root=False):
    for child in src_element.xpathEval("./*"):
        if child.nodePath() in _REPLACES:
            new_child = _REPLACES[child.nodePath()](child)
        else:
            new_child = _REPLACES[None](child)
        if new_child is None:
            logger.warn("Didn't get replacement for %s", child.nodePath())
            continue
        if root:
            dst_parent.setRootElement(new_child)
        else:
            dst_parent.addChild(new_child)
        copy_replace_tree(child, new_child)

def place_defaults(root, app="installation"):
    for default_key in sorted(_DEFAULTS.keys(), key=lambda x: x[1]):
        application, xpath = default_key
        if application != app:
            continue
        if len(root.xpathEval(xpath)) == 0:
            elem = _DEFAULTS[default_key](root)
            tag_elements(elem, xpath, "_default_for")
