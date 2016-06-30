import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getselected
from anabot.runtime.translate import set_languages_by_name, tr
from anabot.runtime.errors import TimeoutError

import time

_local_path = '/installation/welcome'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

def set_language(local_node):
    locales = getnode(local_node, "table", "Locales")
    set_languages_by_name(getselected(locales)[0].name)

@handle_act('')
def base_handler(element, app_node, local_node):
    welcome = getnode(app_node, "panel", "WELCOME")
    set_language(welcome)
    default_handler(element, app_node, welcome)

@handle_chck('')
def base_check(element, app_node, local_node):
    try:
        welcome = getnode(app_node, "panel", "WELCOME", visible=False)
        return True
    except TimeoutError:
        return False

@handle_act('/beta_dialog')
def beta_dialog_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    try:
        beta_dialog = getnode(app_node, "dialog", "Beta Warn")
        if dialog_action:
            button_text = "I want to _proceed."
        else:
            button_text = "I want to _exit."
        button_text = tr(button_text, context="GUI|Welcome|Beta Warn Dialog")
        button = getnode(beta_dialog, "push button", button_text)
        button.click()
    except TimeoutError as e:
        return False
    return True

@handle_act('/continue')
def continue_handler(element, app_node, local_node):
    getnode(local_node, "push button", "_Continue").click()

@handle_act('/language')
def language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang_search = getnode(local_node, node_type="text")
    gui_lang_search.typeText(lang)
    gui_lang = getnode(local_node, "table cell", lang)
    gui_lang.click()
    set_language(local_node)

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
    set_language(local_node)

@handle_chck('/locality')
def locality_check(element, app_node, local_node):
    locality = get_attr(element, "value")
    gui_locality = getnode(local_node, "table cell",
                           ".* ({0})".format(locality))
    return gui_locality.selected
