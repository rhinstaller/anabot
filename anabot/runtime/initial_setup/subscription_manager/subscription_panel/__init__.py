import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError


_local_path = '/initial_setup/subscription_manager/subscription_panel'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def subscription_panel_handler(element, app_node, local_node):
    panel = local_node
    default_handler(element, app_node, panel)
    return (True, None)

@handle_chck('')
def subscription_panel_chck(element, app_node, local_node):
    return action_result(element)   

@handle_act('/subscriptions')
def empty_handler(element, app_node, local_node):
    pass

@handle_chck('/subscriptions')
def subscriptions_chck(element, app_node, local_node):
    subscriptions_table = getnode(local_node, 'table', 'Selected Subscriptions Table')
    cells = getnodes(subscriptions_table, 'table cell')[:3]
    sub_name, sub_type, sub_count = [c.text for c in cells]
    if sub_name != "":
        return (True, "Possible subscription found %s (%s) %s" % (sub_name, sub_type, sub_count))
    return (False, "No subscription found")

@handle_act('/back')
def back_handler(element, app_node, local_node):
    back_button = getnode(local_node.parent.parent, "push button", tr("Back"))
    back_button.click()

@handle_act('/attach')
def attach_button_handler(element, app_node, local_node):
    attach_button = getnode(local_node.parent.parent, "push button", tr("Attach"))
    attach_button.click()
    # attaching subscriptions takes some time, wait until progress bar disappears
    try:
        getnode(local_node, 'progress bar', 'register_progressbar')
    except TimeoutError:
        #ToDo show warning that progress bar was not visible
        pass
    getnode(local_node, 'progress bar', 'register_progressbar', visible=False, timeout=float('inf'))

@handle_chck('/attach')
def attach_button_chck(element, app_node, local_node):
    try:
        result_label = getnode(local_node, 'label', tr('Registration with Red Hat Subscription Management is Done!'))
    except TimeoutError:
        return (False, "Cannot find success message.")
    return (True, 'Registration was successfull.')

