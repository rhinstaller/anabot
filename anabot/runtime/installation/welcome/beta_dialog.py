from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import get_attr, getnode
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError, NonexistentError

_local_path = '/installation/welcome/beta_dialog'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

@handle_act('')
def beta_dialog_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    try:
        beta_dialog = getnode(app_node, "dialog", "Beta Warn")
        if dialog_action:
            button_text = "I want to _proceed."
        else:
            button_text = "I want to _exit."
        button_text = tr(button_text, context="GUI|Welcome|Beta Warn Dialog")
        button = getnode(beta_dialog, "push button", button_text)
        button.click()
    except TimeoutError:
        return False
    except NonexistentError:
        return False
    return True

