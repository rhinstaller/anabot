# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')
import teres 
reporter = teres.Reporter.get_reporter()

from fnmatch import fnmatchcase

from anabot.conditions import is_distro_version
from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getnodes, getparent, getsibling, disappeared
from anabot.runtime.translate import tr
from anabot.runtime.errors import TimeoutError
from anabot.runtime.installation.common import done_handler
from anabot.runtime.actionresult import NotFoundResult as NotFound
from anabot.runtime.actionresult import ActionResultFail as Fail
import re
from time import sleep

from . import common, additional_repo, proxy
from .common import repo_url, repo_url_protocol, repo_url_type, source_context, PASS

_local_path = '/installation/hub/installation_source'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

@handle_act('')
def base_handler(element, app_node, local_node):
    try:
        spoke_selector = getnode(
            local_node, "spoke selector",
            tr("_Installation Source", context="GUI|Spoke"),
            timeout=300,
        )
    except TimeoutError:
        return (False, "Couldn't find installation source selector in hub.")

    spoke_selector.click()
    try:
        spoke_label = getnode(app_node, "label", tr("INSTALLATION SOURCE"))
        local_node = getparent(spoke_label, "filler")
    except TimeoutError:
        return (False, "Couldn't find installation source spoke.")
    additional_repo.initial_repos = additional_repo.get_repolist(local_node)
    default_handler(element, app_node, local_node)
    try:
        return done_handler(element, app_node, local_node)
    except TimeoutError:
        return NotFound("Couldn't find \"Done\" button.")

@handle_chck('')
def base_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    if disappeared(app_node, "label", tr("INSTALLATION SOURCE")):
        return True
    else:
        return (False, "Done button (probably in installation source spoke) is still visible.")

def source_manipulate(element, app_node, local_node, dry_run):
    source_map = {
        "media":    "_Auto-detected installation media:",
        "cdn":      "Red Hat _CDN",
        "iso":      "_ISO file:",
        "network":  "_On the network:",
    }
    source_type = get_attr(element, "type")
    try:
        source_type_name = tr(source_map[source_type], context=source_context)
    except KeyError:
        return (False, "Unknown source type: %s" % source_type)

    try:
        source_question_label = getnode(
            local_node,
            "label",
            tr("Which installation source would you like to use?")
        )
    except TimeoutError:
        return NotFound("installation source question label")
    try:
        source_radio = getsibling(
            source_question_label,
            1,
            "radio button", 
            source_type_name
        )
        if source_radio is None:
            return (False, "Couldn't find radio button: %s" % source_type_name)
    except TimeoutError:
        return (False, "Couldn't find radio button: %s" % source_type_name)

    if not dry_run:
        source_radio.click()
    else:
        return source_radio.checked

@handle_act('/source')
def source_handler(element, app_node, local_node):
    return source_manipulate(element, app_node, local_node, False)

@handle_chck('/source')
def source_check(element, app_node, local_node):
    return source_manipulate(element, app_node, local_node, True)

def verify_media_manipulate(element, app_node, local_node, dry_run):
    try:
        validate_button = getnode(local_node, "push button", tr("_Verify", context=source_context))
        if dry_run:
            return action_result(element)
    except TimeoutError:
        return NotFound("validate button", where="media verification dialog")
    if not dry_run:
        validate_button.click()

    try:
        check_dialog = getparent(getnode(app_node, "label", tr("MEDIA VERIFICATION")), "dialog")
    except TimeoutError:
        return NotFound("media check dialog or MEDIA VERIFICATION label", where="media verification dialog")
    
    try:
        progressbar = getnode(check_dialog, "progress bar")
    except TimeoutError:
        return NotFound("verification progress bar", where="media verification dialog")

    # wait up to 10 minutes for the verification to finish
    timeout = 10*60
    interval = 10
    for attempt in range(timeout // interval + 1):
        if progressbar.value < 1:
            logger.info("Waiting for media validation to finish (%d s remaining)." % (timeout - attempt*interval))
            sleep(interval)
        else:
            logger.info("Media validation complete.")
            break
    else:
        return Fail("Media validation hasn't finished within expected timeframe (%d s)." % timeout)
    
    try:
        validation_label = getsibling(progressbar, -1, "label")
    except TimeoutError:
        return NotFound("validation result label", where="media verification dialog")

    try:
        done_button = getnode(check_dialog, "push button", tr("_Done", context="GUI|Software Source|Media Check Dialog"))
    except TimeoutError:
        return NotFound("Done button", where="media verification dialog")

    if validation_label.name == tr("This media is good to install from."):
        result = PASS
    else:
        result = Fail("Media check failed ('%s')." % validation_label.name)
    done_button.click()
    return result

@handle_act('/verify_media')
def verify_media_handler(element, app_node, local_node):
    return verify_media_manipulate(element, app_node, local_node, False)

@handle_chck('/verify_media')
def verify_media_check(element, app_node, local_node):
    return verify_media_manipulate(element, app_node, local_node, True)


def iso_device_manipulate(element, app_node, local_node, dry_run):
    return Fail("Not implemented")

@handle_act('/iso_device')
def iso_device_handler(element, app_node, local_node):
    return iso_device_manipulate(element, app_node, local_node, False)

@handle_chck('/iso_device')
def iso_device_check(element, app_node, local_node):
    return iso_device_manipulate(element, app_node, local_node, True)

def choose_iso_manipulate(element, app_node, local_node, dry_run):
    return Fail("Not implemented")

@handle_act('/choose_iso')
def choose_iso_handler(element, app_node, local_node):
    return choose_iso_manipulate(element, app_node, local_node, False)

@handle_chck('/choose_iso')
def choose_iso_check(element, app_node, local_node):
    return choose_iso_manipulate(element, app_node, local_node, True)

def verify_iso_manipulate(element, app_node, local_node, dry_run):
    return Fail("Not implemented")

@handle_act('/verify_iso')
def verify_iso_handler(element, app_node, local_node):
    return verify_iso_manipulate(element, app_node, local_node, False)

@handle_chck('/verify_iso')
def verify_iso_check(element, app_node, local_node):
    return verify_iso_manipulate(element, app_node, local_node, True)


def main_repo_url_manipulate(element, app_node, local_node, dry_run):
    url = get_attr(element, "value")
    try:
        url_type_label = getnode(local_node, "label", tr("URL type:", context=source_context), visible=None, sensitive=None)
        repo_url_field = getnode(getparent(url_type_label), "text", sensitive=None)
    except TimeoutError:
        return NotFound("URL type label or main URL input field")
    if not repo_url_field.sensitive:
        return Fail("Main repo URL input field is not active (sensitive), possibly due to wrong installation source selected.")
    return repo_url(repo_url_field, url, dry_run)

@handle_act('/main_repo_url')
def main_repo_url_handler(element, app_node, local_node):
    return main_repo_url_manipulate(element, app_node, local_node, False)

@handle_chck('/main_repo_url')
def main_repo_url_check(element, app_node, local_node):
    return main_repo_url_manipulate(element, app_node, local_node, True)

def main_repo_protocol_manipulate(element, app_node, local_node, dry_run):
    protocol = get_attr(element, "value")
    try:
        url_type_label = getnode(local_node, "label", tr("URL type:", context=source_context), visible=None, sensitive=None)
        protocol_combo = getnodes(getparent(url_type_label), "combo box", visible=None, sensitive=None)[1]
    except TimeoutError:
        return NotFound("URL type label or main URL protocol combo box")
    if not protocol_combo.visible:
        return Fail("Main repo protocol combo box is not visible, possibly due to wrong installation source selected.")
    return repo_url_protocol(app_node, protocol_combo, protocol, dry_run)

@handle_act('/main_repo_url_protocol')
def main_repo_protocol_handler(element, app_node, local_node):
    return main_repo_protocol_manipulate(element, app_node, local_node, False)

@handle_chck('/main_repo_url_protocol')
def main_repo_protocol_check(element, app_node, local_node):
    return main_repo_protocol_manipulate(element, app_node, local_node, True)

def main_repo_type_manipulate(element, app_node, local_node, dry_run):
    protocol = get_attr(element, "value")
    try:
        url_type_label = getnode(local_node, "label", tr("URL type:", context=source_context), visible=None, sensitive=None)
        type_combo = getnodes(getparent(url_type_label), "combo box", visible=None, sensitive=None)[0]
    except TimeoutError:
        return NotFound("URL type label or main repo protocol combo box")
    if not type_combo.visible or not type_combo.sensitive:
        return Fail("Main repo protocol combo box is not visible or active, possibly due to selected protocol.")
    return repo_url_type(app_node, type_combo, protocol, dry_run)

@handle_act('/main_repo_type')
def main_repo_type_handler(element, app_node, local_node):
    return main_repo_type_manipulate(element, app_node, local_node, False)

@handle_chck('/main_repo_type')
def main_repo_type_check(element, app_node, local_node):
    return main_repo_type_manipulate(element, app_node, local_node, True)
