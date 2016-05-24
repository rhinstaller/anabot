# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getparent
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, comps_tr

_local_path = '/installation/hub/package_selection'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    spoke_selector = getnode(local_node, "spoke selector",
                             tr("_SOFTWARE SELECTION", context="GUI|Spoke"))
    spoke_selector.click()
    spoke_label = getnode(app_node, "label", tr("SOFTWARE SELECTION"))
    local_node = getparent(spoke_label, "filler")
    default_handler(element, app_node, local_node)
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()

@handle_chck('')
def base_check(element, app_node, local_node):
    pass

@handle_act('/environment')
def environment_handler(element, app_node, local_node):
    pass

@handle_chck('/environment')
def environment_check(element, app_node, local_node):
    pass

@handle_act('/addon')
def addon_handler(element, app_node, local_node):
    pass

@handle_chck('/addon')
def addon_check(element, app_node, local_node):
    pass
