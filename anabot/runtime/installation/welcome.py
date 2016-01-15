import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getselected
from anabot.runtime.translate import set_languages_by_name

import time

_local_path = '/installation/welcome'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    welcome = getnode(app_node, "panel", "WELCOME")
    default_handler(element, app_node, welcome)
    locales = getnode(welcome, "table", "Locales")
    set_languages_by_name(getselected(locales)[0].name)
    getnode(welcome, "push button", "_Continue").click()

@handle_act('/language')
def language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang_search = getnode(local_node, node_type="text")
    gui_lang_search.typeText(lang)
    gui_lang = getnode(local_node, "table cell", lang)
    gui_lang.click()

@handle_chck('/language')
def language_check(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang = getnode(local_node, "table cell", lang)
    return gui_lang.selected

@handle_act('/locality')
def locality_handler(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell", ".* (%s)" % locality)
    gui_locality_first = getnode(local_node, "table cell", ".* (.*)")
    gui_locality_first.click()
    time.sleep(1)
    while not gui_locality.selected:
        gui_locality_first.parent.keyCombo("Down")
        time.sleep(1)

@handle_chck('/locality')
def locality_check(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell",
                           ".* ({0})".format(locality))
    return gui_locality.selected
