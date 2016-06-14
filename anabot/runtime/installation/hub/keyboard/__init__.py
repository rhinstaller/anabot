# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

import langtable

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getsibling, TimeoutError
from anabot.runtime.translate import tr, keyboard_tr
from .layouts import layout_name

_local_path = '/installation/hub/keyboard'
_local_layout_path = '/installation/hub/keyboard/layout'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
def layout_act(path):
    def decorator(func):
        handle_action(_local_path + path, func)
        return handle_action(_local_layout_path + path, func)
    return decorator

def layout_chck(path):
    def decorator(func):
        handle_check(_local_path + path, func)
        return handle_check(_local_layout_path + path, func)
    return decorator

@handle_act('')
def base_handler(element, app_node, local_node):
    keyboard_label = tr("_KEYBOARD", context="GUI|Spoke")
    keyboard = getnode_scroll(app_node, "spoke selector", keyboard_label)
    keyboard.click()
    local_node = getnode(app_node, "panel", tr("KEYBOARD LAYOUT"))
    default_handler(element, app_node, local_node)
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()

@handle_chck('')
def base_check(element, app_node, local_node):
    pass

def toolbar(local_node):
    return getnode(local_node, "tool bar")

@handle_act('/add_layout')
def layout_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    tool_bar = toolbar(local_node)
    add_button = getnode(tool_bar, "push button",
                         tr("_Add layout", context="GUI|Keyboard Layout"))
    add_button.click()
    dialog = getnode(app_node, "dialog", tr("Add Layout"))
    layouts = getnode(dialog, "table", tr("Available Layouts"))
    layout = getnode_scroll(layouts, "table cell", layout_name(name))
    layout.click()
    if dialog_action:
        button_text = tr("_Add", context="GUI|Keyboard Layout|Add Layout")
    else:
        button_text = tr("_Cancel", context="GUI|Keyboard Layout|Add Layout")
    dialog_button = getnode(dialog, "push button", button_text)
    dialog_button.click()

@handle_chck('/add_layout')
def layout_check(element, app_node, local_node):
    pass

@handle_act('/layout')
def layout_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    table = getnode(local_node, "table", tr("Selected Layouts"))
    layout = getnode_scroll(table, "table cell", layout_name(name))
    layout.click()
    default_handler(element, app_node, local_node)

@handle_chck('/layout')
def layout_check(element, app_node, local_node):
    pass

# position must be inside layout since it needs to know which layout to
# operate with
@handle_act('/layout/position')
def layout_handler(element, app_node, local_node):
    pass

@handle_chck('/layout/position')
def layout_check(element, app_node, local_node):
    pass

def do_toolbar(local_node, button_name):
    tool_bar = toolbar(local_node)
    # try, except, return False...
    button = getnode(tool_bar, "push button",
                     tr(button_name, context="GUI|Keyboard Layout"))
    button.click()
    return True

@layout_act('/remove')
def remove_handler(element, app_node, local_node):
    return do_toolbar(local_node, "_Remove layout")

@layout_chck('/remove')
def remove_check(element, app_node, local_node):
    pass

@layout_act('/move_up')
def move_up_handler(element, app_node, local_node):
    return do_toolbar(local_node, "Move selected layout _up")

@layout_chck('/move_up')
def move_up_check(element, app_node, local_node):
    pass

@layout_act('/move_down')
def move_down_handler(element, app_node, local_node):
    return do_toolbar(local_node, "Move selected layout _down")

@layout_chck('/move_down')
def move_down_check(element, app_node, local_node):
    pass

@layout_act('/show')
def show_handler(element, app_node, local_node):
    toolbar_result = do_toolbar(local_node, "_Preview layout")
    dialog = getnode(app_node, "dialog")
    # TODO: Check dialog name!
    getnode(dialog, "drawing area") # something may be drawn
    getnode(dialog, "push button", tr("Close")).click()
    return toolbar_result

@layout_chck('/show')
def show_check(element, app_node, local_node):
    pass

@layout_act('/test')
def test_handler(element, app_node, local_node):
    pass

@layout_chck('/test')
def test_check(element, app_node, local_node):
    pass

@layout_act('/options')
def _handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    options_button = getnode(local_node, "push button",
                             tr("_Options", context="GUI|Keyboard Layout"))
    options_button.click()

    dialog = getnode(app_node, "dialog", tr("Layout Options"))
    table = getnode(dialog, "table")
    default_handler(element, app_node, table)

    button_context = "GUI|Keyboard Layout|Switching Options"
    if dialog_action:
        button_text = tr("_OK", context=button_context)
    else:
        button_text = tr("_Cancel", context=button_context)
    getnode(dialog, "push button", button_text).click()

@layout_chck('/options')
def _check(element, app_node, local_node):
    pass

@layout_act('/options/shortcut')
def _handler(element, app_node, local_node):
    name = get_attr(element, "name")
    enable = get_attr(element, "action", "enable") == "enable"
    cell = getnode_scroll(local_node, "table cell", keyboard_tr(name))
    checkbox = getsibling(cell, -1, "table cell")
    if checkbox.checked != enable:
        checkbox.click()

@layout_chck('/options/shortcut')
def _check(element, app_node, local_node):
    pass
