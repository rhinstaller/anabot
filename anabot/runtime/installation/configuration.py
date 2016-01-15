import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, TimeoutError
from anabot.runtime.translate import tr

_local_path = '/installation/configuration'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def base_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    logger.debug("WAITING FOR REBOOT")
    reboot_button = getnode(app_node, "push button",
                            tr("_Reboot", context="GUI|Progress"),
                            timeout=float("inf"))
    reboot_button.click()

@handle_act('/root_password')
def root_password_handler(element, app_node, local_node):
    root_password_spoke = getnode(app_node, "spoke selector",
                                  tr("_ROOT PASSWORD", context="GUI|Spoke"))
    root_password_spoke.click()
    try:
        root_password_panel = getnode(app_node, "panel", tr("ROOT PASSWORD"))
    except TimeoutError:
        return (False, "Root password spoke not found")
    default_handler(element, app_node, root_password_panel)

@handle_act('/root_password/password')
def root_password_text_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text", tr("Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_act('/root_password/confirm_password')
def root_password_confirm_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    password_entry = getnode(local_node, "password text",
                             tr("Confirm Password"))
    password_entry.click()
    password_entry.typeText(value)

@handle_act('/root_password/done')
def root_password_done_handler(element, app_node, local_node):
    try:
        root_password_done = getnode(local_node, "push button",
                                     tr("_Done", False))
    except TimeoutError:
        return (False, "Done button not found or not clickable")

    root_password_done.click()
    return True # done for password found and was clicked
