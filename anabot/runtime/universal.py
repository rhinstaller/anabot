import tempfile
import subprocess

import logging
logger = logging.getLogger('anabot')

from .decorators import handle_action, handle_check
from .actionresult import ActionResultFail, ActionResultNone, ActionResultPass

from .functions import get_attr, dump

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

SCRIPT_FAIL = "Script ended with non-zero return code: %s"
@handle_action("script")
def script_handler(element, app_node, local_node):
    interpret = get_attr(element, "interpret", "/bin/bash")
    content = element.content
    with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
        tmpfile.write(content)
        tmpfile.flush()
        filename = tmpfile.name
        retcode = subprocess.call([interpret, filename])
    if retcode == 0:
        return ActionResultPass()
    return ActionResultFail(SCRIPT_FAIL, retcode) % retcode
