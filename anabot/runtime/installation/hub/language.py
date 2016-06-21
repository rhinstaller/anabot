"""
Handle language support spoke.
"""

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, getnodes, getparent, get_attr, getnode_scroll
from anabot.runtime.functions import scrollto
from anabot.runtime.functions import TimeoutError
from anabot.runtime.translate import tr
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail

import time
import fnmatch
import logging

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


@handle_act('/language')
def language_handler(element, app_node, local_node):
    pass


@handle_act('/language/locality')
def locality_handler(element, app_node, local_node):
    pass


@handle_act('/done')
def done_handler(element, app_node, local_node):
    """Leave language support spoke."""
    lang_label = getnode(app_node, "label", tr("LANGUAGE SUPPORT"))
    lang_panel = getparent(lang_label, "panel")

    done_button = getnode(lang_panel,
                          "push button",
                          tr("_Done",
                             drop_underscore=False))
    time.sleep(10)
    done_button.click()
