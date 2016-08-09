import tempfile
import subprocess

import logging
logger = logging.getLogger('anabot')

from .decorators import handle_action, handle_check
from .actionresult import ActionResultFail, ActionResultNone, ActionResultPass

from .functions import dump

@handle_action("debug_stop")
def debug_stop_handler(element, app_node, local_node):
    from time import sleep
    import os
    RESUME_FILEPATH = '/var/run/anabot/resume'
    sleep(5)
    dump(app_node, '/tmp/dogtail.dump')
    logger.debug('DEBUG STOP at %s, touch %s to resume',
                 element.nodePath(), RESUME_FILEPATH)
    while not os.path.exists(RESUME_FILEPATH):
        sleep(0.1)
    os.remove(RESUME_FILEPATH)
    return True
