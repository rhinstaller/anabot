from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.runtime.functions import getnode, get_attr, clear_text
from anabot.runtime.actionresult import ActionResultPass, ActionResultFail, NotFoundResult
from anabot.runtime.errors import TimeoutError
from anabot.conditions import is_distro_version, is_distro_version_ge
from anabot.runtime.default import default_handler
from .common import set_language
import logging

logger = logging.getLogger('anabot')

_local_path = '/installation/welcome/language'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

@handle_act('')
def language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang_search = getnode(local_node, node_type="text")
    # the whole application seems to be out of focus under some unknown circumstances, so clicking
    # into the input field first ensures that the text will be entered properly
    gui_lang_search.click()
    clear_text(gui_lang_search)
    gui_lang_search.typeText(lang)
    gui_lang = getnode(local_node, "table cell", lang)
    gui_lang.click()
    set_language(local_node)
    default_handler(element, app_node, local_node)

@handle_chck('', cond=is_distro_version('rhel', 7))
def language_check_7(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang = getnode(local_node, "table cell", lang)
    return gui_lang.selected

@handle_chck('', cond=is_distro_version_ge('rhel', 8) or is_distro_version_ge('fedora', 35))
def language_check_8(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang = getnode(local_node, "table cell", lang).parent
    return gui_lang.selected

@handle_act('/locale')
def locale_manipulate(element, app_node, local_node, dry_run):
    locale = get_attr(element, "value")
    try:
        locale_table = getnode(app_node, "table", "Locales")
        locale_cell = getnode(locale_table, "table cell", locale)
    except TimeoutError:
        return NotFoundResult("locale table or table cell")
    if dry_run:
        return ActionResultPass if locale_cell.selected else ActionResultFail
    logger.info("Selecting locale '%s'" % locale)
    locale_cell.click()
    set_language(local_node)
    return ActionResultPass()

@handle_act('/locale')
def locale_handler(element, app_node, local_node):
    return locale_manipulate(element, app_node, local_node, False)

@handle_chck('/locale')
def locale_check(element, app_node, local_node):
    return locale_manipulate(element, app_node, local_node, True)
