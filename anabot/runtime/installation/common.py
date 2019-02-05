# Functions for clicking on done button
from anabot.conditions import is_distro_version
from anabot.runtime.functions import getnode
from anabot.runtime.translate import tr

def done_handler(element, app_node, local_node):
    if is_distro_version('rhel', 7):
        return done_handler7(element, app_node, local_node)
    # have RHEL-8 default (for Fedora)
    return done_handler8(element, app_node, local_node)

def done_handler7(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()
    return True

def done_handler8(element, app_node, local_node):
    done_button = getnode(
        local_node, "push button",
        tr("_Done", False, context="GUI|Spoke Navigation")
    )
    done_button.click()
    return True

