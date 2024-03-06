import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from fnmatch import fnmatchcase
from time import sleep

from anabot.conditions import is_distro_version_ge, is_distro_version_lt, is_distro_version
from anabot.variables import get_variable
from anabot.runtime.decorators import handle_action, handle_check, check_action_result
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import getnode, is_alive, TimeoutError
from anabot.runtime.workarounds import wait_for_line
from anabot.runtime.translate import tr

# submodules
from . import connect_to_redhat, datetime, keyboard, partitioning, software_selection, oscap_addon, language, system_purpose, installation_source, kdump_addon

def _wait_for_depsolve(initial=True):
    if initial and is_distro_version_ge('rhel', 8) and get_variable('interactive_kickstart', '0') == '1':
        # The depsolving doesn't seem to be happening during kickstart
        # installation on RHEL-8.
        return
    if initial and get_variable('interactive_kickstart', '0') == '0' and get_variable('repo_on_cmdline') == '0':
        # Installation is not kickstart and repo is not configured on cmdline, initial depsolving shouldn't be happening.
        return
    reporter.log_info("Waiting for package depsolving. Timeout is 10 minutes")

    filename = '/tmp/packaging.log'
    waitline = ".*DEBUG yum.verbose.YumBase: Depsolve time:.*"

    # Temporary change to also support Fedora 34.
    if ((is_distro_version_ge('rhel', 8) and is_distro_version_lt('rhel', 10))
            or is_distro_version('fedora', 34)):
        waitline = '.* INF packaging: checking dependencies: success'

    if is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 35):
        waitline = '.*The software selection has been resolved.*'

    if wait_for_line(filename, waitline, 600):
        reporter.log_info("Depsolving finished, nothing should block anaconda main thread now (GTK/ATK) now")
    else:
        reporter.log_info("Depsolving _NOT_ finished, it may happen, that anaconda main thread (GTK/ATK) will be blocked in future and prevent anabot working properly.")

@handle_action('/installation/hub')
def hub_handler(element, app_node, local_node):
    _wait_for_depsolve()
    local_node = getnode(app_node, "panel", tr("INSTALLATION SUMMARY"))
    def wait_for_animation_end():
        # wait for animation end
        for i in range(50):
            if is_alive(local_node) and local_node.position[1] == 0:
                # animation ended
                break
            sleep(0.1)
        else:
            reporter.log_error("It seems that (re)entering hub animation is still in progress.")
    default_handler(element, app_node, local_node, waitfunc=wait_for_animation_end)

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
