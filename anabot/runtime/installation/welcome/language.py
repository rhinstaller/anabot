from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import getnode, get_attr
from .common import set_language

_local_path = '/installation/welcome/language'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang_search = getnode(local_node, node_type="text")
    gui_lang_search.typeText(lang)
    gui_lang = getnode(local_node, "table cell", lang)
    gui_lang.click()
    set_language(local_node)

@handle_chck('')
def language_check(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang = getnode(local_node, "table cell", lang)
    return gui_lang.selected
