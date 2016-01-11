import logging
logger = logging.getLogger('anabot')

import time
from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler

# submodules
from . import welcome, hub, configuration

@handle_action('/installation')
def installation_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
