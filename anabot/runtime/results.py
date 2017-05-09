import libxml2
from .actionresult import ActionResultNone

RESULTS = {}

def action_result(node_path, implicit_result=ActionResultNone()):
    if isinstance(node_path, libxml2.xmlNode):
        node_path = node_path.nodePath()
    result = RESULTS.get(node_path, implicit_result)
    if isinstance(result, ActionResultNone):
        result = implicit_result
    return result
