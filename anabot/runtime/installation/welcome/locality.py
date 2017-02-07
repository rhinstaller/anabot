from anabot.runtime.functions import getnode, get_attr
from anabot.runtime.decorators import handle_action, handle_check
from .common import set_language

_local_path = '/installation/welcome/locality'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def locality_handler(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell", ".* (%s)" % locality)
    gui_locality_first = getnode(local_node, "table cell", ".* (.*)")
    gui_locality_first.click()
    time.sleep(1)
    while not gui_locality.selected:
        gui_locality_first.parent.keyCombo("Down")
        time.sleep(1)
    set_language(local_node)

@handle_chck('')
def locality_check(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell",
                           ".* ({0})".format(locality))
    return gui_locality.selected
