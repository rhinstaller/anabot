import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import getnode
from anabot.runtime.translate import tr

from dogtail.predicate import GenericPredicate

# submodules
from . import license
#, subscription_manager

@handle_action('/initial_setup/hub')
def hub_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)
    # ToDo
    # find FINISH CONFIGURATION button and click it
