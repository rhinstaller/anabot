import logging
logger = logging.getLogger('anabot')

import re

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import get_attr, getnode
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.errors import TimeoutError

_local_path = '/installation/welcome/os_name'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def os_name_handler(element, app_node, local_node):
    # Check-only element, there's nothing to do in the action phase.
    return None

@handle_chck('')
def os_name_check(element, app_node, local_node):
    value = get_attr(element, "value")
    if value is None:
        return Fail("No 'value' attribute specified for os_name check.")
    # Anaconda upper-cases the product name in the welcome screen labels and
    # appends the version, which we don't care about (matched by a wildcard).
    # getnode matches the name as a regex, so we can wildcard the version.
    #   "WELCOME TO %(name)s %(version)s."         (pyanaconda welcome.py)
    #   "%(productName)s %(productVersion)s INSTALLATION"  (pyanaconda helpers.py)
    name = re.escape(value.upper())
    welcome_pattern = "WELCOME TO %s .*" % name
    installation_pattern = "%s .* INSTALLATION" % name
    try:
        getnode(app_node, "label", welcome_pattern)
    except TimeoutError:
        return Fail("No label matching %r found on the welcome screen."
                    % welcome_pattern)
    try:
        getnode(app_node, "label", installation_pattern)
    except TimeoutError:
        return Fail("No label matching %r found on the welcome screen."
                    % installation_pattern)
    return Pass()
