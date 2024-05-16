# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

import fnmatch
import random
import six

from anabot.runtime.decorators import make_prefixed_handle_action, make_prefixed_handle_check
from anabot.conditions import is_distro_version, is_distro_version_ge, is_distro_version_lt
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getnodes, getsibling, combo_scroll, \
    type_text, press_key, getparent
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, datetime_tr
from anabot.runtime.actionresult import notfound as notfound_new, ActionResultFail as Fail, \
    ActionResultPass as Pass, NotFoundResult as NotFound
from anabot.runtime.installation.common import done_handler

def notfound(*args, **kwargs):
    return (False, notfound_new(*args, **kwargs))

_local_path = '/installation/hub/datetime'
handle_act = make_prefixed_handle_action(_local_path)
handle_chck = make_prefixed_handle_check(_local_path)

@handle_act('', cond=is_distro_version('rhel', 7))
def base_handler_7(element, app_node, local_node):
    datetime_label = tr("DATE & TIME")
    try:
        datetime = getnode_scroll(app_node, "spoke selector", datetime_label)
    except TimeoutError:
        return notfound('"DATE & TIME"', where="main hub")
    datetime.click()
    try:
        datetime_panel = getnode(app_node, "panel", tr("DATE & TIME"))
    except TimeoutError:
        return notfound("DATE & TIME spoke")
    default_handler(element, app_node, datetime_panel)
    return done_handler(element, app_node, datetime_panel)

@handle_chck('', cond=is_distro_version('rhel', 7))
def base_check_7(element, app_node, local_node):
    if action_result(element)[0] != False:
        return action_result(element)
    try:
        getnode(app_node, "panel", tr("DATE & TIME"), visible=False)
        return True
    except TimeoutError:
        return (False, "Datetime spoke is still visible.")

@handle_act('', cond=is_distro_version_ge('rhel', 8))
def base_handler_8(element, app_node, local_node):
    datetime_label = tr("_Time & Date", context="GUI|Spoke")
    try:
        datetime = getnode_scroll(app_node, "spoke selector", datetime_label)
    except TimeoutError:
        return notfound('"DATE & TIME"', where="main hub")
    datetime.click()
    try:
        datetime_panel = getnode(app_node, "panel", tr("TIME & DATE"))
    except TimeoutError:
        return notfound("DATE & TIME spoke")
    default_handler(element, app_node, datetime_panel)
    return done_handler(element, app_node, datetime_panel)

@handle_chck('', cond=is_distro_version_ge('rhel', 8))
def base_check_8(element, app_node, local_node):
    if action_result(element)[0] != False:
        return action_result(element)
    try:
        getnode(app_node, "panel", tr("_Time & Date", context="GUI|Spoke"), visible=False)
        return True
    except TimeoutError:
        return (False, "Datetime spoke is still visible.")

@handle_act('/region')
def region_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    region_name = datetime_tr(value)
    try:
        region_label = getnode(local_node, "label",
                               tr("_Region:", context="GUI|Date and Time"))
    except TimeoutError:
        return notfound("label", whose="Region combo box")
    region_combo = getsibling(region_label, 1, "combo box")
    # can't do this better (simple) way
    region_combo.actions['press'].do()
    try:
        combo_window = getnode(app_node, "window")
    except TimeoutError:
        return notfound("window", whose="Region combo box")
    try:
        region_item = getnode(combo_window, "menu item", region_name)
    except TimeoutError:
        return notfound('"%s"'%region_name, where="Region combo box")
    region_item.click()

@handle_chck('/region')
def region_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    # I don't know why, but the region is not translated in name of widget
    #region_name = datetime_tr(value)
    region_name = value
    try:
        region_label = getnode(local_node, "label",
                               tr("_Region:", context="GUI|Date and Time"))
    except TimeoutError:
        return notfound("label", whose="Region combo box")
    region_combo = getsibling(region_label, 1, "combo box")
    if six.u(region_combo.name) == six.u(region_name):
        return True
    return (False, "Expected region: '%s', saw: '%s'" % (region_name, region_combo.name))

@handle_act('/city')
def city_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    city_name = datetime_tr(value)
    try:
        city_label = getnode(local_node, "label",
                             tr("_City:", context="GUI|Date and Time"))
    except TimeoutError:
        return notfound("label", whose="City combo box")
    city_combo = getsibling(city_label, 1, "combo box")
    # can't do this better (simple) way
    city_combo.actions['press'].do()
    try:
        combo_window = getnode(app_node, "window")
    except TimeoutError:
        return notfound("window", whose="City combo box")
    try:
        city_item = getnode(combo_window, "menu item", city_name)
    except TimeoutError:
        return notfound('"%s"'%city_name, where="City combo box")
    combo_scroll(city_item, click=1)

@handle_chck('/city')
def city_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    # I don't know why, but the city is not translated in name of widget
    #city_name = datetime_tr(value)
    city_name = value
    try:
        city_label = getnode(local_node, "label",
                             tr("_City:", context="GUI|Date and Time"))
    except TimeoutError:
        return notfound("label", whose="City combo box")
    city_combo = getsibling(city_label, 1, "combo box")
    if six.u(city_combo.name) == six.u(city_name):
        return True
    return (False, "Expected city: '%s', saw: '%s'" % (city_name, city_combo.name))

def ntp_manipulate(element, app_node, local_node, dryrun):
    ntp_state = {
        True: "enabled",
        False: "disabled"
    }
    ntp_mode = {
        True: "automatic",
        False: "manual"
    }
    enable_ntp = get_attr(element, "action", "enable") == "enable"

    if is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40):
        try:
            ntp_toggle = getnode(local_node, "toggle button", tr("Use Network Time"))
        except TimeoutError:
            return NotFound("toggle button", whose="NTP")
        if ntp_toggle.checked != enable_ntp:
            if dryrun:
                return Fail("NTP is %s, expected: %s" %
                    (ntp_state[ntp_toggle.checked], ntp_state[enable_ntp])
                )
            else:
                ntp_toggle.click()
    # RHEL-10+/Fedora 40+ uses radio buttons to set automatic/manual mode instead of
    # a toggle switch
    else:
        if enable_ntp:
            button_text = tr("_Automatic date & time")
        else:
            button_text = tr("_Manual date & time")

        try:
            radiobutton = getnode(local_node, "radio button", button_text)
        except TimeoutError:
            return NotFound("'%s' radio button" % button_text, where="Time & Date spoke")
        if not radiobutton.checked:
            if dryrun:
                return Fail(
                    """Date & time mode is {mode_found} (NTP {state_found}), expected {mode_expected} """
                    """({state_expected} mode)""".format(
                        mode_found=ntp_mode[radiobutton.checked], state_found=ntp_state[radiobutton.checked],
                        mode_expected=ntp_mode[enable_ntp], state_expected=ntp_state[enable_ntp]
                    )
                )
            else:
                radiobutton.click()
    return Pass()

@handle_act('/ntp')
def ntp_handler(element, app_node, local_node):
    return ntp_manipulate(element, app_node, local_node, False)

@handle_chck('/ntp')
def ntp_check(element, app_node, local_node):
    return ntp_manipulate(element, app_node, local_node, True)

@handle_act('/ntp_settings')
def ntp_settings_handler(element, app_node, local_node):
    if is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40):
        return Fail("NTP settings handler/check not (yet) implemented for RHEL-10+ or Fedora 40+.")
    dialog_action = get_attr(element, 'dialog', 'accept')
    if dialog_action == 'accept':
        button_name = tr('_OK', context="GUI|Date and Time|NTP")
    elif dialog_action == 'dialog':
        button_name = tr('_Cancel', context="GUI|Date and Time|NTP")
    try:
        ntp_button = getnode(local_node, "push button", tr("Configure NTP"))
    except TimeoutError:
        return notfound("button", whose="Configure NTP dialog")
    ntp_button.click()
    try:
        local_node = getnode(app_node, "dialog", tr("Configure NTP"))
    except TimeoutError:
        return notfound("dialog", whose="Configure NTP")
    default_handler(element, app_node, local_node)
    try:
        tmp_filler = getnode(local_node, 'filler', recursive=False)
    except TimeoutError:
        return notfound("filler", where="NTP dialog")
    try:
        buttons_filler = getnodes(tmp_filler, 'filler', recursive=False)[-1]
    except TimeoutError:
        return notfound("filler", where="NTP dialog")
    try:
        dialog_button = getnode(buttons_filler, "push button", button_name)
    except TimeoutError:
        return notfound("button '%s'"%button_name, where="NTP Dialog")
    dialog_button.click()
    return True

@handle_act('/ntp_settings/add')
def ntp_settings_add_handler(element, app_node, local_node):
    hostname = get_attr(element, "hostname")
    try:
        input_node = getnode(local_node, "text", tr("New NTP Server"))
    except TimeoutError:
        return notfound("input for new server", where="NTP dialog")
    input_node.click()
    input_node.typeText(hostname)
    try:
        add_button = getnode(local_node, "push button", tr("Add NTP Server"))
    except TimeoutError:
        return notfound("button for adding server", where="NTP dialog")
    add_button.click()

@handle_chck('/ntp_settings/add')
def ntp_settings_add_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    hostname = six.u(get_attr(element, "hostname"))
    try:
        table = getnode(local_node, "table")
    except TimeoutError:
        return notfound("table with NTP servers", where="NTP dialog")
    for candidate in getnodes(table, "table cell")[::3]:
        if fnmatch.fnmatchcase(six.u(candidate.name), hostname):
            return True
    return notfound("specified ntp server", where="NTP dialog")

@handle_act('/ntp_settings/rename')
def ntp_settings_rename_handler(element, app_node, local_node):
    old = get_attr(element, "old")
    new = get_attr(element, "new")
    try:
        table = getnode(local_node, "table")
    except TimeoutError:
        return notfound("table with NTP servers", where="NTP dialog")
    try:
        node = getnode(table, "table cell", old)
    except TimeoutError:
        return notfound("specified ntp server", where="NTP dialog")
    node.doubleClick()
    type_text(new)
    press_key('enter')
    return True

@handle_chck('/ntp_settings/rename')
def ntp_settings_rename_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    new = get_attr(element, "new")
    try:
        table = getnode(local_node, "table")
    except TimeoutError:
        return notfound("table with NTP servers", where="NTP dialog")
    try:
        node = getnode(table, "table cell", new)
        return True
    except TimeoutError:
        return notfound("renamed ntp server", where="NTP dialog")

def ntp_settings_enable_manipulate(element, app_node, local_node, enable, dry_run):
    hostname = get_attr(element, "hostname")
    try:
        table = getnode(local_node, "table")
    except TimeoutError:
        return notfound("table with NTP servers", where="NTP dialog")
    ok = True
    for candidate in getnodes(table, "table cell")[::3]:
        if fnmatch.fnmatchcase(six.u(candidate.name), hostname):
            checkbox_cell = getsibling(candidate, 2, "table cell")
            if enable != checkbox_cell.checked:
                if not dry_run:
                    checkbox_cell.click()
                else:
                    ok = False
    if dry_run:
        if ok:
            return True
        else:
            return (False, "Not all ntp servers are %s" % (enable and "enabled" or "disabled"))

@handle_act('/ntp_settings/enable')
def ntp_settings_enable_handler(element, app_node, local_node):
    ntp_settings_enable_manipulate(element, app_node, local_node, True, False)

@handle_chck('/ntp_settings/enable')
def ntp_settings_enable_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    return ntp_settings_enable_manipulate(element, app_node, local_node, True, True)

@handle_act('/ntp_settings/disable')
def ntp_settings_disable_handler(element, app_node, local_node):
    ntp_settings_enable_manipulate(element, app_node, local_node, False, False)

@handle_chck('/ntp_settings/disable')
def ntp_settings_disable_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    return ntp_settings_enable_manipulate(element, app_node, local_node, False, True)

@handle_act('/time', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def time_handler_9(element, app_node, local_node):
    try:
        datetime_node = getnode(local_node, "filler", tr("Set Date & Time"))
    except TimeoutError:
        return notfound("filler", whose="date and time settings")
    try:
        time_node = getnode(datetime_node, "panel")
    except TimeoutError:
        return notfound("panel", whose="time settings")
    default_handler(element, app_node, time_node)
    return True

@handle_chck('/time', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def time_check_9(element, app_node, local_node):
    # nothing to check here
    return Pass()

@handle_act('/time', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def time_handler_10(element, app_node, local_node):
    try:
        date_label = getnode(local_node, "label", tr("Date"))
        datetime_panel = getparent(date_label, "panel")
    except TimeoutError:
        return NotFound("Date and Time panel")
    default_handler(element, app_node, datetime_panel)
    return Pass()

@handle_chck('/time', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def time_check_10(element, app_node, local_node):
    # nothing to check here
    return Pass()

@handle_act('/time/hours')
def time_hours_handler(element, app_node, local_node):
    value = int(get_attr(element, "value"))
    try:
        hours_label = getnode(local_node, "label", tr("Hours"))
    except TimeoutError:
        return notfound("label", whose="hours settings")
    try:
        hours_minus = getnode(local_node, "push button", tr("Hour Down"))
    except TimeoutError:
        return notfound("button", whose="decrease hour")
    try:
        hours_plus = getnode(local_node, "push button", tr("Hour Up"))
    except TimeoutError:
        return notfound("button", whose="increase hour")
    for i in range(int(hours_label.text), value):
        hours_plus.click()
    for i in range(int(hours_label.text), value, -1):
        hours_minus.click()

@handle_chck('/time/hours')
def time_hours_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    try:
        hours_label = getnode(local_node, "label", tr("Hours"))
    except TimeoutError:
        return notfound("label", whose="hours settings")
    if hours_label.text == value:
        return True
    return (False, "Hour didn't match desired value")

@handle_act('/time/minutes')
def time_minutes_handler(element, app_node, local_node):
    value = int(get_attr(element, "value"))
    try:
        minutes_label = getnode(local_node, "label", tr("Minutes"))
    except TimeoutError:
        return notfound("label", whose="minutes settings")
    try:
        minutes_minus = getnode(local_node, "push button", tr("Minutes Down"))
    except TimeoutError:
        return notfound("button", whose="decrease minute")
    try:
        minutes_plus = getnode(local_node, "push button", tr("Minutes Up"))
    except TimeoutError:
        return notfound("button", whose="increase minute")
    for i in range(int(minutes_label.text), value):
        minutes_plus.click()
    for i in range(int(minutes_label.text), value, -1):
        minutes_minus.click()

@handle_chck('/time/minutes')
def time_minutes_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    try:
        minutes_label = getnode(local_node, "label", tr("Minutes"))
    except TimeoutError:
        return notfound("label", whose="minutes settings")
    if minutes_label.text == value:
        return True
    return (False, "Minute didn't match desired value")

def time_format_manipulate(element, app_node, local_node, dry_run):
    value = get_attr(element, "value")
    if is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40):
            local_node = getsibling(local_node, 1, "panel")
    if value == "24":
        wanted_text = tr("24-_hour", context="GUI|Date and Time")
    elif value == "12":
        wanted_text = tr("_AM/PM", context="GUI|Date and Time")
    else:
        return (False, "Format '%s' not recognized" % value)
    try:
        wanted_radio = getnode(local_node, "radio button", wanted_text)
    except TimeoutError:
        return notfound("radio button '%s'"%wanted_text, where="time settings")
    if not wanted_radio.checked:
        if not dry_run:
            wanted_radio.click()
        else:
            return (False, "Format '%s' not selected" % value)
    return True

@handle_act('/time/format')
def time_format_handler(element, app_node, local_node):
    time_format_manipulate(element, app_node, local_node, False)

@handle_chck('/time/format')
def time_format_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    return time_format_manipulate(element, app_node, local_node, True)

@handle_act('/time/ampm')
def time_ampm_handler(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = tr(get_attr(element, "value"))
    am = tr("AM")
    pm = tr("PM")
    for x in (am, pm):
        try:
            ampm_label = getnode(local_node, "label", x)
            break
        except TimeoutError:
            pass
    else:
        return notfound("neither AM, nor PM label", where="time settings")
    buttons = getnodes(local_node, "push button", tr("AM/PM Up"))
    buttons += getnodes(local_node, "push button", tr("AM/PM Down"))
    random_button = random.choice(buttons)
    if value != six.u(ampm_label.text):
        random_button.click()
    return True

@handle_chck('/time/ampm')
def time_ampm_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = tr(get_attr(element, "value"))
    try:
        ampm_label = getnode(local_node, "label", value)
        return True
    except TimeoutError:
        return notfound("correct label for '%s'" % value)

@handle_act('/date', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_handler_9(element, app_node, local_node):
    def get_menuitems_count(combo):
        return len(getnodes(combo, "menu item", visible=None))
    try:
        datetime_node = getnode(local_node, "filler", tr("Set Date & Time"))
    except TimeoutError:
        return notfound("filler", whose="date and time settings")
    combos = sorted(getnodes(datetime_node, "combo box"), key=get_menuitems_count)
    if len(combos) != 3:
        return notfound("all date, month and year combo boxes")
    default_handler(element, app_node, combos)
    return True

@handle_chck('/date', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_check_9(element, app_node, local_node):
    return Pass()

@handle_act('/date', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_handler_10(element, app_node, local_node):
    try:
        date_label = getnode(local_node, "label", tr("Date"))
        datetime_panel = getparent(date_label, "panel")
    except TimeoutError:
        return NotFound("Date and Time panel")
    default_handler(element, app_node, datetime_panel)
    return Pass()

@handle_chck('/date', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_check_10(element, app_node, local_node):
    # nothing to check here
    return Pass()

@handle_act('/date/month', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_month_handler_9(element, app_node, local_node):
    value = get_attr(element, "value")
    month_combo = local_node[0]
    month_combo.click()
    try:
        window = getnode(app_node, "window")
    except TimeoutError:
        return notfound("window", whose="month combo box")
    try:
        item = getnode(window, "menu item", value)
    except TimeoutError:
        press_key('esc')
        return (False, "Specified month is not available")
    combo_scroll(item, click=1)
    return True

@handle_chck('/date/month', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_month_check_9(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    month_combo = local_node[0]
    if month_combo.name == value:
        return True
    return (False, "Expected month: %s, saw: %s" % (value, month_combo.name))

def handle_date(element, app_node, local_node, dryrun, combo_nr, combo_name):
    value = get_attr(element, "value")
    try:
        combo = getnodes(local_node, "combo box")[combo_nr]
        if not dryrun:
            combo.click()
            item = getnode(combo, "menu item", value)
            combo_scroll(item, click=1)
    except TimeoutError:
        return NotFound("%s combo box or menu item" % combo_name.lower())
    if dryrun:
        if combo.name != value:
            return Fail("{} value ({}) is different from expected one ({})".format(
                combo_name.lower(), combo.name, value
            ))
    return Pass()

@handle_act('/date/month', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_month_handler_10(element, app_node, local_node):
    return handle_date(element, app_node, local_node, False, 0, "Month")

@handle_chck('/date/month', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_month_check_10(element, app_node, local_node):
    return handle_date(element, app_node, local_node, True, 0, "Month")


@handle_act('/date/day', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_day_handler_9(element, app_node, local_node):
    value = get_attr(element, "value")
    day_combo = local_node[1]
    day_combo.click()
    try:
        window = getnode(app_node, "window")
    except TimeoutError:
        return notfound("window", whose="day combo box")
    try:
        item = getnode(window, "menu item", value)
    except TimeoutError:
        press_key('esc')
        return (False, "Specified day is not available (maybe wrong month)")
    combo_scroll(item, click=1)
    return True

@handle_chck('/date/day', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_day_check_9(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    day_combo = local_node[1]
    if day_combo.name == value:
        return True
    return (False, "Expected day: %s, saw: %s" % (value, day_combo.name))

@handle_act('/date/day', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_day_handler_10(element, app_node, local_node):
    return handle_date(element, app_node, local_node, False, 1, "Day")

@handle_chck('/date/day', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_day_check_10(element, app_node, local_node):
    return handle_date(element, app_node, local_node, True, 1, "Day")


@handle_act('/date/year', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_year_handler_9(element, app_node, local_node):
    value = get_attr(element, "value")
    year_combo = local_node[2]
    year_combo.click()
    try:
        window = getnode(app_node, "window")
    except TimeoutError:
        return notfound("window", whose="year combo box")
    try:
        item = getnode(window, "menu item", value)
    except TimeoutError:
        return (False, "Specified year is not available.")
    combo_scroll(item, click=1)

@handle_chck('/date/year', cond=is_distro_version_lt('rhel', 10) or is_distro_version_lt('fedora', 40))
def date_year_check_9(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    value = get_attr(element, "value")
    year_combo = local_node[2]
    if year_combo.name == value:
        return True
    return (False, "Expected year: %s, saw: %s" % (value, year_combo.name))

@handle_act('/date/year', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_year_handler_10(element, app_node, local_node):
    return handle_date(element, app_node, local_node, False, 2, "Year")

@handle_chck('/date/year', cond=is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40))
def date_year_check_10(element, app_node, local_node):
    return handle_date(element, app_node, local_node, True, 2, "Year")
