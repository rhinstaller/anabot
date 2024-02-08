from anabot.conditions import is_distro, is_anaconda_version_lt
from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import get_attr, getnode
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError, NonexistentError

_local_path = '/installation/welcome/beta_dialog'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

def _is_button_with_dot():
    # The terminating dots were removed from the labels on the buttons on the Beta dialog.
    # RHEL: https://github.com/rhinstaller/anaconda/pull/4771/commits/3a28c203cccc572db498669d76e57ceb8bbd772d
    if is_distro('rhel') and is_anaconda_version_lt('34.25.3.4'):
        return True
    # Fedora: https://github.com/rhinstaller/anaconda/commit/64219c599759bfec1e538fe30d4a6f6819a3c65d
    if is_distro('fedora') and is_anaconda_version_lt('39.4'):
        return True
    return False

@handle_act('')
def beta_dialog_handler(element, app_node, local_node):
    dialog_action = get_attr(element, "dialog", "accept") == "accept"
    try:
        beta_dialog = getnode(app_node, "dialog", tr("Beta Warn"))  # Beta Dialog's name needs to be translated
        if dialog_action:
            button_text = "I want to _proceed." if _is_button_with_dot() else "I want to _proceed"
        else:
            button_text = "I want to _exit." if _is_button_with_dot() else "I want to _exit"
        button_text = tr(button_text, context="GUI|Welcome|Beta Warn Dialog")
        button = getnode(beta_dialog, "push button", button_text)
        button.click()
    except TimeoutError:
        return False
    except NonexistentError:
        return False
    return True

