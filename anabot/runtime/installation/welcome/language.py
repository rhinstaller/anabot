from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.runtime.functions import getnode, get_attr
from anabot.conditions import is_distro_version, is_distro_version_ge
from .common import set_language

_local_path = '/installation/welcome/language'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

@handle_act('')
def language_handler(element, app_node, local_node):
    lang = get_attr(element, "value")
    gui_lang_search = getnode(local_node, node_type="text")
    gui_lang_search.typeText(lang)
    gui_lang = getnode(local_node, "table cell", lang)
    gui_lang.click()
    set_language(local_node)

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
