from anabot.runtime.errors import TimeoutError
from anabot.runtime.functions import getnode, getnode_scroll, get_attr
from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.actionresult import ActionResultPass, ActionResultFail, NotFoundResult
from .common import set_language

import time

_local_path = '/installation/welcome/locality'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def locality_handler(element, app_node, local_node):
    locality = get_attr(element, "value")
    try:
        gui_locality = getnode_scroll(local_node, "table cell", ".* (%s)" % locality)
    except TimeoutError:
        return NotFoundResult("locality table cell", whose=locality)
    gui_locality.click()
    set_language(local_node)
    return ActionResultPass()

LOCALITY_NOT_SELECTED = ActionResultFail("Locality '%s' is not selected.")
@handle_chck('')
def locality_check(element, app_node, local_node):
    locality = get_attr(element, "value")
    try:
        gui_locality = getnode(local_node, "table cell",
                               ".* ({0})".format(locality))
    except TimeoutError:
        return NotFoundResult("locality table cell", whose=locality)
    if gui_locality.selected:
        return ActionResultPass()
    return LOCALITY_NOT_SELECTED % locality
