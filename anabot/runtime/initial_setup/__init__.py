import logging
logger = logging.getLogger('anabot')

import time
from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode
from anabot.runtime.translate import tr

# submodules
from . import license, subscription_manager

@handle_action('/initial_setup')
def initial_setup_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_action('/initial_setup/finish')
def finish_handler(element, app_node, local_node):
    button = getnode(app_node, 'push button', tr('FINISH CONFIGURATION'))
    button.click()

@handle_action('/initial_setup/quit')
def quit_handler(element, app_node, local_node):
    button = getnode(app_node, 'push button', tr('QUIT'))
    button.click()
    default_handler(element, app_node, local_node)

@handle_action('/initial_setup/quit/no')
def quit_no_handler(element, app_node, local_node):
    dialog = getnode(app_node, 'dialog', 'Quit')
    button = getnode(dialog, 'push button', tr('No'))
    button.click()

@handle_action('/initial_setup/quit/yes')
def quit_yes_handler(element, app_node, local_node):
    dialog = getnode(app_node, 'dialog', 'Quit')
    button = getnode(dialog, 'push button', tr('Yes'))
    button.click()

