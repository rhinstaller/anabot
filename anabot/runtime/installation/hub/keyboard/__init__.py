# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
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

PASS = Pass()
SPOKE_SELECTOR_NOT_FOUND = Fail("Didn't find active spoke selector for Keyboard layout.")
SPOKE_NOT_FOUND = Fail("Didn't find panel for Keyboard layout.")
DONE_NOT_FOUND = Fail("Didn't find \"Done\" button.")

@handle_act('')
def base_handler(element, app_node, local_node):
    keyboard_label = tr("_KEYBOARD", context="GUI|Spoke")
    try:
        keyboard = getnode_scroll(app_node, "spoke selector", keyboard_label)
    except TimeoutError:
        return SPOKE_SELECTOR_NOT_FOUND
    keyboard.click()
    try:
        local_node = getnode(app_node, "panel", tr("KEYBOARD LAYOUT"))
    except TimeoutError:
        return SPOKE_NOT_FOUND
    default_handler(element, app_node, local_node)
    try:
        done_button = getnode(local_node, "push button", tr("_Done", False))
    except TimeoutError:
        return DONE_NOT_FOUND
    done_button.click()
    return PASS

@handle_chck('')
def base_check(element, app_node, local_node):
    if action_result(element) == False:
        return action_result(element)
    # TODO: check status of spoke selector
    return PASS

def toolbar(local_node):
    return getnode(local_node, "tool bar")

TOOLBAR_NOT_FOUND = Fail("Didn't find toolbar for keyboard layouts.")
TOOLBAR_BUTTON_NOT_FOUND = Fail("Didn't find toolbar button: %s")
def do_toolbar(local_node, button_name, button_desc=None):
    try:
        tool_bar = toolbar(local_node)
    except TimeoutError:
        return TOOLBAR_NOT_FOUND
    # try, except, return False...
    try:
        button = getnode(tool_bar, "push button",
                         tr(button_name, context="GUI|Keyboard Layout"))
    except TimeoutError:
        if button_desc is None:
            button_desc = button_name
        return TOOLBAR_BUTTON_NOT_FOUND % button_desc
    button.click()
    return PASS

ADD_DIALOG_NOT_FOUND = Fail("Didn't find dialog for adding layout.")
ADD_TABLE_NOT_FOUND = Fail("Didn't find table with layouts in dialog.")
ADD_LAYOUT_NOT_FOUND = Fail("Didn't find desired layout \"%s\" in table.")
ADD_DIALOG_BUTTON_FOUND = Fail("Didn't find desired dialog button.")
@handle_act('/add_layout')
def add_layout_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    do_result = do_toolbar(local_node, "_Add layout")
    if do_result == False:
        return do_result

    try:
        dialog = getnode(app_node, "dialog", tr("Add Layout"))
    except TimeoutError:
        return ADD_DIALOG_NOT_FOUND

    try:
        layouts = getnode(dialog, "table", tr("Available Layouts"))
    except TimeoutError:
        return ADD_TABLE_NOT_FOUND

    try:
        layout = getnode_scroll(layouts, "table cell", layout_name(name))
        layout.click()
    except TimeoutError:
        return ADD_LAYOUT_NOT_FOUND % layout_name(name)

    if dialog_action:
        button_text = tr("_Add", context="GUI|Keyboard Layout|Add Layout")
    else:
        button_text = tr("_Cancel", context="GUI|Keyboard Layout|Add Layout")

    try:
        dialog_button = getnode(dialog, "push button", button_text)
        dialog_button.click()
    except:
        return ADD_DIALOG_BUTTON_FOUND
    return PASS

@handle_chck('/add_layout')
def add_layout_check(element, app_node, local_node):
    pass

LAYOUTS_TABLE_NOT_FOUND = Fail("Didn't find table with layouts")
LAYOUT_NOT_FOUND = Fail("Didn't find desired layout: %s")
@handle_act('/layout')
def layout_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    try:
        table = getnode(local_node, "table", tr("Selected Layouts"))
    except TimeoutError:
        return LAYOUTS_TABLE_NOT_FOUND
    try:
        layout = getnode_scroll(table, "table cell", layout_name(name))
        layout.click()
    except TimeoutError:
        return LAYOUT_NOT_FOUND % layout_name(name)
    default_handler(element, app_node, local_node)
    return PASS

@handle_chck('/layout')
def layout_check(element, app_node, local_node):
    pass

# position must be inside layout since it needs to know which layout to
# operate with
@handle_act('/layout/position')
def layout_position_handler(element, app_node, local_node):
    pass

@handle_chck('/layout/position')
def layout_position_check(element, app_node, local_node):
    pass

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

SHOW_DIALOG_NOT_FOUND = Fail("Didn't find dialog with layout preview.")
SHOW_DRAWING_NOT_FOUND = Fail("Didn't find drawing area in layout preview.")
SHOW_CLOSE_NOT_FOUND = Fail("Didn't find close button in layout preview.")
@layout_act('/show')
def show_handler(element, app_node, local_node):
    toolbar_result = do_toolbar(local_node, "_Preview layout")
    if toolbar_result == False:
        return toolbar_result
    try:
        # TODO: Check dialog name!
        dialog = getnode(app_node, "dialog")
    except TimeoutError:
        return SHOW_DIALOG_NOT_FOUND
    try:
        getnode(dialog, "drawing area") # something may be drawn
    except TimeoutError:
        return SHOW_DRAWING_NOT_FOUND
    try:
        getnode(dialog, "push button", tr("Close")).click()
    except TimeoutError:
        return SHOW_CLOSE_NOT_FOUND
    return PASS

@layout_chck('/show')
def show_check(element, app_node, local_node):
    pass

@layout_act('/test')
def test_handler(element, app_node, local_node):
    pass

@layout_chck('/test')
def test_check(element, app_node, local_node):
    pass

OPTIONS_NOT_FOUND = Fail("Didn't find options button.")
OPTIONS_DIALOG_NOT_FOUND = Fail("Didn't find options dialog.")
OPTIONS_TABLE_NOT_FOUND = Fail("Didn't find table with shortcuts.")
OPTION_NOT_FOUND = Fail("Didn't find desired shortcut: %s")
OPTIONS_DIALOG_BUTTON_NOT_FOUND = Fail("Didn't find desired dialog button: %s")
@layout_act('/options')
def options_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    try:
        options_button = getnode(local_node, "push button",
                                 tr("_Options", context="GUI|Keyboard Layout"))
    except TimeoutError:
        return OPTIONS_NOT_FOUND
    options_button.click()

    try:
        dialog = getnode(app_node, "dialog", tr("Layout Options"))
    except TimeoutError:
        return OPTIONS_DIALOG_NOT_FOUND
    try:
        table = getnode(dialog, "table")
    except TimeoutError:
        return OPTIONS_TABLE_NOT_FOUND
    default_handler(element, app_node, table)

    button_context = "GUI|Keyboard Layout|Switching Options"
    if dialog_action:
        button_text = tr("_OK", context=button_context)
    else:
        button_text = tr("_Cancel", context=button_context)
    try:
        getnode(dialog, "push button", button_text).click()
    except TimeoutError:
        return OPTIONS_DIALOG_BUTTON_NOT_FOUND % button_text

@layout_chck('/options')
def options_check(element, app_node, local_node):
    pass

SHORTCUT_NOT_FOUND = Fail("Didn't find desired shortcut: %s")
@layout_act('/options/shortcut')
def options_shortcut_handler(element, app_node, local_node):
    name = get_attr(element, "name")
    enable = get_attr(element, "action", "enable") == "enable"
    try:
        cell = getnode_scroll(local_node, "table cell", keyboard_tr(name))
    except TimeoutError:
        return SHORTCUT_NOT_FOUND % keyboard_tr(name)
    checkbox = getsibling(cell, -1, "table cell")
    if checkbox.checked != enable:
        checkbox.click()

@layout_chck('/options/shortcut')
def options_shortcut_check(element, app_node, local_node):
    pass
