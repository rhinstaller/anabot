"""
Handle language support spoke.
"""
import fnmatch
import logging

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, getnodes, get_attr
from anabot.runtime.functions import scrollto, getnode_scroll
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail

logger = logging.getLogger('anabot')
_local_path = '/installation/hub/language_spoke'


def handle_act(suffix):
    """Helper function to avoid typing a lot."""
    return handle_action(_local_path + suffix)


def handle_chck(suffix):
    """Helper function to avoid typing a lot."""
    return handle_check(_local_path + suffix)


PASS = Pass()
SPOKE_SELECTOR_NOT_FOUND = Fail(
    "Didn't find active spoke selector for Language support.")
SPOKE_NOT_FOUND = Fail("Didn't find panel Language support.")
DONE_NOT_FOUND = Fail("Didn't find \"Done\" button.")


@handle_act('')
def base_handler(element, app_node, local_node):
    """Handle <language_spoke> tag and process its options."""
    lang_label = tr("_LANGUAGE SUPPORT", context="GUI|Spoke")

    try:
        lang = getnode_scroll(app_node, "spoke_selector", lang_label)
    except TimeoutError:
        return SPOKE_SELECTOR_NOT_FOUND

    lang.click()

    try:
        local_node = getnode(app_node, "panel", tr("LANGUAGE SUPPORT"))
    except TimeoutError:
        return SPOKE_NOT_FOUND

    default_handler(element, app_node, local_node)

    # Click the Done button.
    try:
        done_button = getnode(local_node, "push button", tr("_Done", False))
    except TimeoutError:
        return DONE_NOT_FOUND

    done_button.click()

    return PASS


@handle_chck("")
def base_check(element, app_node, local_node):
    """Base check for <language> tag."""
    if action_result(element) == False:
        return action_result(element)
    return PASS


@handle_act('/language')
def language_handler(element, app_node, local_node):
    """Handle <language> tag and process its options."""
    lang = get_attr(element, "select")
    lang_table = getnodes(local_node, "table")[1]

    matched = False

    for lang_node in getnodes(lang_table, "table cell", visible=None)[::4]:
        if fnmatch.fnmatchcase(lang_node.name, lang):
            matched = True
            scrollto(lang_node)
            lang_node.click()
            default_handler(element, app_node, local_node)

    if not matched:
        return False

    return True


@handle_chck('/language')
def language_check(element, app_node, local_node):
    """Check the <language> settings."""
    pass


@handle_act('/language/locality')
def locality_handler(element, app_node, local_node):
    """Handle <locality> tag and process its options."""
    pass


@handle_chck('/language/locality')
def locality_check(element, app_node, local_node):
    """Check <locality>."""
    pass
