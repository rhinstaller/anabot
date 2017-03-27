# -*- coding: utf-8 -*-
import time
import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode, getnodes, TimeoutError, getparent, getsibling, log_screenshot, _DEFAULT_TIMEOUT
from anabot.runtime.translate import tr, gtk_tr
from anabot.runtime.hooks import run_posthooks
from anabot.runtime.variables import get_variable

_local_path = '/installation/configuration'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

import root_password, create_user

@handle_act('')
def base_handler(element, app_node, local_node):
    timeout = _DEFAULT_TIMEOUT
    if get_variable('interactive_kickstart', False):
        timeout = 180
    settings_panel = getnode(app_node, "panel", tr("CONFIGURATION"), timeout=timeout)
    default_handler(element, app_node, settings_panel)

@handle_act('/wait_until_complete')
def wait_until_complete_handler(element, app_node, local_node):
    reporter.log_debug("Looking for installation progress bar.")
    try:
        progress = getnode(local_node, "progress bar")
    except:
        return (False, "Couldn't find progress bar")
    reporter.log_debug("WAITING FOR REBOOT")
    stable_counter = 0
    while stable_counter < 5:
        time.sleep(1)
        if progress.value >= 1:
            stable_counter += 1
        else:
            stable_counter = 0
    return True

@handle_act('/eula_notice')
def eula_notice_handler(element, app_node, local_node):
    reporter.log_info("Eula notice has only check, no action.")

@handle_chck('/eula_notice')
def eula_notice_check(element, app_node, local_node):
    try:
        warn_bar = getnode(local_node, "info bar", gtk_tr('Warning'))
    except TimeoutError:
        return (False, "Couldn't find warning bar containing eula notice.")
    try:
        # This probably needs to be changed for Fedora
        eula_text = tr("Use of this product is subject to the license agreement found at %s") % "/usr/share/redhat-release/EULA"
        getnode(warn_bar, "label", eula_text)
    except TimeoutError:
        reporter.log_info("Following labels were found in place where eula notice was expected:")
        for label_node in getnodes(warn_bar, "label"):
            reporter.log_info(label_node.text)
        reporter.log_info("End of labels.")
        reporter.log_info(u"Expected eula text was: %s" % eula_text)
        return (False, "Warning bar doesn't contain label with correct text")
    return True

@handle_act('/reboot')
def reboot_handler(element, app_node, local_node):
    try:
        reboot_button = getnode(local_node, "push button",
                                tr("_Reboot", context="GUI|Progress"),
                                timeout=15)
    except TimeoutError:
        return (False, "Couldn't find clickable Reboot button.")

    run_posthooks()
    reporter.test_end()
    reboot_button.click()

