import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getparents
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
<<<<<<< 56ef4ab98274fbe5c27ccc5bb57bc0e1bfe42c31
=======
from time import sleep
>>>>>>> initial setup - changes in account_panel


_local_path = '/initial_setup/subscription_manager/account_panel'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def account_panel_handler(element, app_node, local_node):
    user_panel = local_node
    default_handler(element, app_node, user_panel)
    return (True, None)

@handle_chck('')
def account_panel_check(element, app_node, local_node):
    return action_result(element)

@handle_act('/login')
def username_handler(element, app_node, local_node):
    login = get_attr(element, 'value')
    login_input = getnode(local_node, 'text', 'account_login')
    login_input.typeText(login)

@handle_chck('/login')
def username_chck(element, app_node, local_node):
    username = get_attr(element, 'value')
    username_input = getnode(local_node, 'text', 'account_login')
    return username_input.text == username

@handle_act('/password')
def password_handler(element, app_node, local_node):
    password = get_attr(element, 'value')
    password_input = getnode(local_node, 'password text', 'account_password')
    password_input.typeText(password)

# it is not possible to get password back from the widget via ATK
# only check which makes sense is to check that password is not readable
<<<<<<< 56ef4ab98274fbe5c27ccc5bb57bc0e1bfe42c31
@handle_chck('/password')
def password_check(element, app_node, local_node):
    password = get_attr(element, 'value')
    password_input = getnode(local_node, 'password text', 'account_password')
    BLACK_CIRCLE = u'\u25cf'
    return len(password)*BLACK_CIRCLE == unicode(password_input.text, 'utf-8')
=======
# but it is not implemented yet (ToDo)
>>>>>>> initial setup - changes in account_panel

@handle_act('/system_name')
def system_name_handler(element, app_node, local_node):
    name = get_attr(element, 'value')
    system_input = getnode(local_node, 'text', 'consumer_name')
    system_input.typeText(name)

@handle_chck('/system_name')
def system_name_chck(element, app_node, local_node):
    name = get_attr(element, 'value')
    system_input = getnode(local_node, 'text', 'consumer_name')
    # ToDo unicode issue in comparison
    return system_input.text == name

@handle_act('/back')
def back_handler(element, app_node, local_node):
    back_button = getnode(local_node.parent.parent, "push button", tr("Back"))
    back_button.click()

@handle_chck('/back')
def back_check(element, app_node, local_node):
    sm_panels = getnode(app_node, 'page tab list', 'register_notebook')
    try:
        login_input = getnode(sm_panels, 'text', 'account_login', visible=False)
    except TimeoutError:
        return (False, "Account panel is still visible")
    return True

@handle_act('/register')
def next_handler(element, app_node, local_node):
    next_button = getnode(local_node.parent.parent, "push button", tr("Register"))
    next_button.click()
    # registering can last some time, so wait for progressbar to show and disappear
    try:
        getnode(local_node, 'progress bar', 'register_progressbar')
    except TimeoutError:
        # will raise TimeoutError in case invisible progress bar is not found
        # that probably means there is no progress bar at all
        getnode(local_node, 'progress bar', 'register_progressbar', visible=False)
    getnode(local_node, 'progress bar', 'register_progressbar', visible=False, timeout=float('inf'))

@handle_chck('/register')
def account_panel_back_check(element, app_node, local_node):
    sm_panels = getnode(app_node, 'page tab list', 'register_notebook')
    try:
        login_input = getnode(sm_panels, 'text', 'account_login', visible=False)
    except TimeoutError:
        return (False, "Account panel is still visible")
    return True

