import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from fnmatch import fnmatchcase
from time import sleep

from anabot.conditions import is_distro_version_ge
from anabot.variables import get_variable
from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, TimeoutError
from anabot.runtime.workarounds import wait_for_line
from anabot.runtime.translate import tr

# submodules
from . import datetime, keyboard, partitioning, software_selection, oscap_addon, language, system_purpose

def _wait_for_depsolve(initial=True):
    if initial and is_distro_version_ge('rhel', 8) and get_variable('interactive_kickstart', '0') == '1':
        # The depsolving doesn't seem to be happening during kickstart
        # installation on RHEL-8.
        return
    if initial and get_variable('interactive_kickstart', '0') == '0' and get_variable('repo_on_cmdline') == '0':
        # Installation is not kickstart and repo is not configured on cmdline, initial depsolving shouldn't be happening.
        return
    reporter.log_info("Waiting for package depsolving. Timeout is 10 minutes")
    waitline = ".*DEBUG yum.verbose.YumBase: Depsolve time:.*"
    if is_distro_version_ge('rhel', 8):
        waitline = '.* INF packaging: checking dependencies: success'
    if wait_for_line('/tmp/packaging.log', waitline, 600):
        reporter.log_info("Depsolving finished, nothing should block anaconda main thread now (GTK/ATK) now")
    else:
        reporter.log_info("Depsolving _NOT_ finished, it may happen, that anaconda main thread (GTK/ATK) will be blocked in future and prevent anabot working properly.")

@handle_action('/installation/hub')
def hub_handler(element, app_node, local_node):
    _wait_for_depsolve()
    local_node = getnode(app_node, "panel", tr("INSTALLATION SUMMARY"))
    default_handler(element, app_node, local_node)

@handle_check('/installation/hub')
@check_action_result
def hub_check(element, app_node, local_node):
    # TODO: check that the hub is not visible anymore
    return True

@handle_action('/installation/hub/begin_installation')
def begin_installation_handler(element, app_node, local_node):
    try:
        begin_button = getnode(app_node, "push button",
                               tr("_Begin Installation", context="GUI|Summary"),
                               timeout=60
        )
    except TimeoutError:
        return (False, 'Couln\'t find clickable "Begin installation" button.')
    begin_button.click()
    return True

@handle_check('/installation/hub/begin_installation')
def begin_installation_check(element, app_node, local_node):
    if action_result(element) != None:
        logger.debug('begin_installation returns action_result')
        return action_result(element)
    try:
        begin_button = getnode(
            app_node,
            "push button",
            tr("_Begin Installation", context="GUI|Summary"),
            sensitive=None
        )
    except TimeoutError:
        return (False, 'Couln\'t find "Begin installation" button.')
    for i in range(5):
        if begin_button.sensitive:
            return True
        sleep(1)
    return (False, '"Begin installation" button is not clickable')
