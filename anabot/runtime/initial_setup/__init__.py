import logging
logger = logging.getLogger('anabot')

import time
from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler

# submodules
from . import license, subscription_manager

@handle_action('/initial_setup')
def initial_setup_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_action('/initial_setup/finish')
def initial_setup_finish_handler(element, app_node, local_node):
    # ToDo
    # find FINISH CONFIGURATION button and click it
    pass

