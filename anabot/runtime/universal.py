import os
import tempfile
import subprocess

import logging
logger = logging.getLogger('anabot')

import teres
reporter = teres.Reporter.get_reporter()

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
    dump(local_node, '/tmp/dogtail-local.dump')
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
    log_name = get_attr(element, "log_name")
    stdin = open('/dev/null')
    stdout = None
    stderr = None
    if log_name is not None:
        log_name = "script-%s.log" % log_name
        log_path = os.path.join('/var/run/anabot', log_name)
        log_file = file(log_path, 'w')
        logger.debug('Going to log script output in file named: %s', log_name)
        stdout = log_file
        stderr = subprocess.STDOUT
    content = element.content
    with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
        tmpfile.write(content)
        tmpfile.flush()
        filename = tmpfile.name
        process = subprocess.Popen(
            [interpret, filename],
            stdin = stdin,
            stdout = stdout,
            stderr = stderr
        )
        process.wait()
        retcode = process.returncode
    if log_name is not None:
        log_file.close()
        reporter.send_file(log_path)
    if retcode == 0:
        return ActionResultPass()
    return ActionResultFail(SCRIPT_FAIL, retcode) % retcode
