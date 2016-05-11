"""
Handle language support spoke.
"""

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode, getnodes, getparent
from anabot.runtime.translate import tr

import time

import logging
logger = logging.getLogger('anabot')

_local_path = '/installation/hub/language_spoke'


def handle_act(suffix):
    """Helper function to avoid typing a lot."""
    return handle_action(_local_path + suffix)


def handle_chck(suffix):
    """Helper function to avoid typing a lot."""
    return handle_action(_local_path + suffix)


@handle_act('')
def base_handler(element, app_node, local_node):
    """Handle <language> tag and process its options."""
    lang = getnode(app_node, "spoke selector", tr("LANGUAGE SUPPORT"))
    lang.click()
    lang_label = getnode(app_node, "label", tr("LANGUAGE SUPPORT"))

    lang_filler = getparent(lang_label, "filler")
    lang_panel = getnodes(lang_filler, "panel", recursive=False)[1]

    default_handler(element, app_node, lang_panel)

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
