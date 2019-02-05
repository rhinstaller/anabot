# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')
import fnmatch
import six

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.functions import get_attr, getnode, getnodes, getnode_scroll, getsibling, TimeoutError
from anabot.runtime.translate import tr, keyboard_tr
from anabot.runtime.installation.common import done_handler
from .layouts import layout_name, layout_id, Layouts

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

__last_selected_layout = None
__removed_layout = None
__removed_layouts = []

PASS = Pass()
SPOKE_SELECTOR_NOT_FOUND = NotFound(
    "active spoke selector", "selector_not_found", whose="Keyboard layout"
)
SPOKE_NOT_FOUND = NotFound(
    "panel", "spoke_not_found", whose="Keyboard layout"
)
DONE_NOT_FOUND = NotFound(
    '"Done" button', "done_not_found", where="Keyboard layout spoke"
)

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
        done_handler(element, app_node, local_node)
        return PASS
    except TimeoutError:
        return DONE_NOT_FOUND

@handle_chck('')
@check_action_result
def base_check(element, app_node, local_node):
    # TODO: check status of spoke selector
    return PASS

def toolbar(local_node):
    return getnode(local_node, "tool bar")

TOOLBAR_NOT_FOUND = NotFound(
    "toolbar", "toolbar_not_found", whose="keyboard layouts"
)
TOOLBAR_BUTTON_NOT_FOUND = NotFound(
    "'%s' button", "toolbar_button_not_found", where="toolbar"
)
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

ADD_DIALOG_NOT_FOUND = NotFound(
    "dialog", "dialog_not_found", whose="adding layout"
)
ADD_TABLE_NOT_FOUND = NotFound(
    "table with layouts", "layouts_table_not_found", where="dialog"
)
ADD_LAYOUT_NOT_FOUND = NotFound(
    'desired layout "%s"', "layout_not_found", where="table"
)
ADD_DIALOG_BUTTON_FOUND = NotFound(
    "desired dialog button", "dialog_button_not_found"
)
@handle_act('/add_layout')
def add_layout_handler(element, app_node, local_node, in_dialog=False):
    # TODO: add support for layout name expansion
    name = get_attr(element, "name")
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    if not in_dialog:
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

LAYOUTS_TABLE_NOT_FOUND = NotFound(
    "table with layouts",
    # TODO
)
LAYOUT_NOT_FOUND = NotFound(
    'desired layout: "%s"',
    # TODO
)
def get_layout_node(local_node, name):
    try:
        table = getnode(local_node, "table", tr("Selected Layouts"))
    except TimeoutError:
        return LAYOUTS_TABLE_NOT_FOUND
    try:
        layout = getnode_scroll(table, "table cell", layout_name(name))
    except TimeoutError:
        return LAYOUT_NOT_FOUND % layout_name(name)
    return layout

@handle_chck('/add_layout')
@check_action_result
def add_layout_check(element, app_node, local_node):
    name = get_attr(element, "name")
    layout = get_layout_node(local_node, name)
    if isinstance(layout, Fail):
        return layout # not really layout, but fail
    else:
        return PASS

@handle_act('/replace_layouts')
def replace_layouts_handler(element, app_node, local_node):
    try:
        table = getnode(local_node, "table", tr("Selected Layouts"))
    except TimeoutError:
        return LAYOUTS_TABLE_NOT_FOUND
    getnode(table, "table cell").click()
    while len(getnodes(table, "table cell")) > 1:
        do_result = do_toolbar(local_node, "_Remove layout")
        if do_result == False:
            return do_result
    do_result = do_toolbar(local_node, "_Remove layout")
    if do_result == False:
        return do_result
    return add_layout_handler(element, app_node, local_node, in_dialog=True)

MORE_LAYOUTS_FOUND = Fail("More then one layout was found.")
@handle_chck('/replace_layouts')
@check_action_result
def replace_layouts_check(element, app_node, local_node):
    try:
        table = getnode(local_node, "table", tr("Selected Layouts"))
    except TimeoutError:
        return LAYOUTS_TABLE_NOT_FOUND
    if len(getnodes(table, "table cell")) > 1:
        return MORE_LAYOUTS_FOUND
    return add_layout_check(element, app_node, local_node)

@handle_act('/layout')
def layout_handler(element, app_node, local_node):
    global __last_selected_layout
    name_pattern = get_attr(element, "name")
    matched = False
    for layout_id, layout_name in Layouts.get_instance():
        if not fnmatch.fnmatchcase(layout_id, name_pattern):
            continue
        matched = True
        __last_selected_layout = layout_id
        layout = get_layout_node(local_node, layout_id)
        if isinstance(layout, Fail):
            return layout # not really layout, but fail
        layout.click() # pylint: disable=maybe-no-member
        default_handler(element, app_node, local_node)
    __last_selected_layout = None
    if not matched:
        return LAYOUT_NOT_FOUND % name_pattern
    return PASS

# this shouldn't really happen, but who knows
NO_LAYOUT_FOUND = NotFound(
    'any layout matching pattern: "%s"',
    'no_layout_found',
    where="layouts table"
)
REMOVED_LAYOUT_STILL_PRESENT = Fail(
    'Removed layout "%s : %s" is still present', "removed_layout_present"
)
@handle_chck('/layout')
@check_action_result
def layout_check(element, app_node, local_node):
    name_pattern = get_attr(element, "name")
    matched = False
    logger.debug("Removed layouts: %s", __removed_layouts)
    for layout_id, layout_name in Layouts.get_instance():
        if not fnmatch.fnmatchcase(layout_id, name_pattern):
            continue
        matched = True
        if layout_id in __removed_layouts:
            # check if the layout is not present (just to be sure)
            if not isinstance(get_layout_node(local_node, layout_id), Fail):
                return REMOVED_LAYOUT_STILL_PRESENT % (layout_id, layout_name)
            __removed_layouts.remove(layout_id)
            continue
        layout = get_layout_node(local_node, layout_id)
        if isinstance(layout, Fail):
            return layout # not really layout, but fail
    if not matched:
        return NO_LAYOUT_FOUND % name_pattern
    return PASS

# position must be inside layout since it needs to know which layout to
# operate with
@handle_act('/layout/position')
def layout_position_handler(element, app_node, local_node):
    # TODO
    pass

@handle_chck('/layout/position')
@check_action_result
def layout_position_check(element, app_node, local_node):
    # TODO
    pass

@layout_act('/remove')
def remove_handler(element, app_node, local_node):
    global __removed_layout
    __removed_layout = __last_selected_layout
    if __removed_layout is None:
        table = getnode(local_node, "table", tr("Selected Layouts"))
        for layout in getnodes(table, "table cell", visible=None):
            if not layout.selected:
                continue
            __removed_layout = layout_id(six.u(layout.name))
            break
    if __removed_layout is not None:
        __removed_layouts.append(__removed_layout)
    logger.debug("Removing layout: %s", __removed_layout)
    return do_toolbar(local_node, "_Remove layout")

# Remove is behaving awkwardly in anaconda. If the layout is last one, dialog
# for new layout pops up.
# Due to this, we're not really able to remove all layouts and then add one.
# This needs to be probably resolved by special element like 'replace_all'

# XML schema needs to define, that remove can be used inside layout element
# only once, and as last child!
LAYOUT_NOT_REMOVED = Fail("")
@layout_chck('/remove')
@check_action_result
def remove_check(element, app_node, local_node):
    global __removed_layout
    if __removed_layout is None:
        return PASS
    result = get_layout_node(local_node, __removed_layout)
    if isinstance(result, Fail):
        __removed_layout = None
        return PASS
    return LAYOUT_NOT_REMOVED

@layout_act('/move_up')
def move_up_handler(element, app_node, local_node):
    return do_toolbar(local_node, "Move selected layout _up")

@layout_chck('/move_up')
@check_action_result
def move_up_check(element, app_node, local_node):
    # TODO
    pass

@layout_act('/move_down')
def move_down_handler(element, app_node, local_node):
    return do_toolbar(local_node, "Move selected layout _down")

@layout_chck('/move_down')
@check_action_result
def move_down_check(element, app_node, local_node):
    # TODO
    pass

SHOW_DIALOG_NOT_FOUND = NotFound(
    "dialog with layout preview",
    # TODO
)
SHOW_DRAWING_NOT_FOUND = NotFound(
    "drawing area",
    # TODO
    where="layout preview"
)
SHOW_CLOSE_NOT_FOUND = NotFound(
    "close button",
    # TODO
    where="layout preview"
)
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
@check_action_result
def show_check(element, app_node, local_node):
    # TODO
    pass

@layout_act('/test')
def test_handler(element, app_node, local_node):
    # TODO
    pass

@layout_chck('/test')
@check_action_result
def test_check(element, app_node, local_node):
    # TODO
    pass

OPTIONS_NOT_FOUND = NotFound(
    "options button",
    # TODO
    whose="layout change shortcuts"
)
OPTIONS_DIALOG_NOT_FOUND = NotFound(
    "options dialog",
    # TODO
    whose="layout change shortcuts"
)
OPTIONS_TABLE_NOT_FOUND = NotFound(
    "table with shortcuts",
    # TODO
    where="shortcuts dialog"
)
OPTIONS_DIALOG_BUTTON_NOT_FOUND = NotFound(
    'desired dialog button: "%s"',
    # TODO
    where="shortcuts dialog"
)
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

# Use just result from action
#@layout_chck('/options')
#@check_action_result
#def options_check(element, app_node, local_node):
#    pass

SHORTCUT_NOT_FOUND = NotFound(
    'desired shortcut: "%s" : "%s"',
    # TODO
    where="shortcuts dialog"
)
SHORTCUT_WRONG_STATE = Fail(
    'Shortcut "%s" is not enabled/disabled but should be.',
    "wrong_state"
)
def options_shortcut_manipulate(element, app_node, local_node, dry_run):
    name = get_attr(element, "name")
    enable = get_attr(element, "action", "enable") == "enable"
    try:
        cell = getnode_scroll(local_node, "table cell", keyboard_tr(name))
    except TimeoutError:
        return SHORTCUT_NOT_FOUND % (name, keyboard_tr(name))
    checkbox = getsibling(cell, -1, "table cell")
    if checkbox.checked != enable:
        if not dry_run:
            checkbox.click()
        else:
            return SHORTCUT_WRONG_STATE % name
    return PASS

@layout_act('/options/shortcut')
def options_shortcut_handler(element, app_node, local_node):
    return options_shortcut_manipulate(element, app_node, local_node, False)

@layout_chck('/options/shortcut')
@check_action_result
def options_shortcut_check(element, app_node, local_node):
    return options_shortcut_manipulate(element, app_node, local_node, True)
