"""
Handle language support spoke.
"""
import fnmatch
import teres

from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, getnodes, get_attr, getparents, getsibling
from anabot.runtime.functions import scrollto, getnode_scroll
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.installation.common import done_handler

reporter = teres.Reporter.get_reporter()

_local_path = '/installation/hub/language_spoke'


def handle_act(suffix):
    """Helper function to avoid typing a lot."""
    return handle_action(_local_path + suffix)


def handle_chck(suffix):
    """Helper function to avoid typing a lot."""
    return handle_check(_local_path + suffix)


PASS = Pass()
SPOKE_SELECTOR_NOT_FOUND = NotFound("active spoke selector",
                                    "selector_not_found",
                                    whose="Language support")
SPOKE_NOT_FOUND = NotFound("panel",
                           "spoke_not_found",
                           whose="Language support")
DONE_NOT_FOUND = NotFound('"Done" button',
                          "done_not_found",
                          where="Language support spoke")


@handle_act('')
def base_handler(element, app_node, local_node):
    """Handle <language_spoke> tag and process its options."""
    lang_label = tr("_LANGUAGE SUPPORT", context="GUI|Spoke")

    try:
        lang = getnode_scroll(app_node, "spoke selector", lang_label)
    except TimeoutError:
        return SPOKE_SELECTOR_NOT_FOUND

    lang.click()

    try:
        lang_spoke_label = getnode(app_node, "label", tr("LANGUAGE SUPPORT"))
    except TimeoutError:
        return SPOKE_NOT_FOUND

    try:
        local_node = getparents(lang_spoke_label, "panel")[2]
    except IndexError:
        return Fail("IndexError while getting language spoke label.")

    default_handler(element, app_node, local_node)

    # Click the Done button.
    try:
        done_handler(element, app_node, local_node)
        return PASS
    except TimeoutError:
        return DONE_NOT_FOUND

@handle_chck('')
@check_action_result
def base_check(element, app_node, local_node):
    """Base check for <language> tag."""
    if action_result(element)[0] == False:
        return action_result(element)
    try:
        spoke_label = getnode(app_node, "label", tr("LANGUAGE SUPPORT"), visible=False)
        return PASS
    except TimeoutError:
        return Fail("Language support spoke is still visible.")

@handle_act('/language')
def language_handler(element, app_node, local_node):
    """Handle <language> tag and process its options."""
    lang = get_attr(element, "select")

    try:
        lang_table = getnodes(local_node, "table")[1]
    except TimeoutError:
        return Fail("Language table not found.")

    matched = False

    for lang_node in getnodes(lang_table, "table cell", visible=None)[2::4]:
        if fnmatch.fnmatchcase(lang_node.name, lang):
            matched = True
            scrollto(lang_node)
            lang_node.click()

            if not lang_node.selected:
                return Fail("Language was not selected.")

            default_handler(element, app_node, local_node)

    if not matched:
        return NotFound('language "{}"'.format(lang), where="language table")

    return PASS


@handle_chck('/language')
@check_action_result
def language_check(element, app_node, local_node):
    """Check the <language> settings."""
    return PASS


@handle_act('/language/locality')
def locality_handler(element, app_node, local_node):
    """Handle <locality> tag and process its options."""
    locality = get_attr(element, "name")

    try:
        locality_table = getnode(local_node, "table")
    except TimeoutError:
        return Fail("Locality table not found.")

    check = get_attr(element, "action", "check") == "check"
    matched = False

    for locality_name in getnodes(locality_table,
                                  "table cell",
                                  visible=None,
                                  sensitive=None)[1::2]:

        if fnmatch.fnmatchcase(locality_name.text, locality):
            matched = True

            locality_checkbox = getsibling(locality_name, -1, "table cell", visible=None, sensitive=None)
            scrollto(locality_name)

            if locality_checkbox.checked != check:
                locality_checkbox.click()

    if not matched:
        return NotFound('locality "{}"'.format(locality), where="locality table")

    return PASS


@handle_chck('/language/locality')
def locality_check(element, app_node, local_node):
    """Check <locality>."""
    locality = get_attr(element, "name")

    try:
        locality_table = getnode(local_node, "table")
    except TimeoutError:
        return Fail("Locality table not found.")

    check = get_attr(element, "action", "check") == "check"

    matched = False

    for locality_name in getnodes(locality_table,
                                  "table cell",
                                  visible=None,
                                  sensitive=None)[1::2]:

        if fnmatch.fnmatchcase(locality_name.text, locality):
            matched = True

            locality_checkbox = getsibling(locality_name, -1, "table cell", visible=None, sensitive=None)
            scrollto(locality_name)

            if locality_checkbox.checked != check:
                Fail("Check failed for {}".format(locality_name))

    if not matched:
        return NotFound('locality "{}"'.format(locality), where="locality table")

    return PASS
