# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

#import pytz

import fnmatch
import random

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getnodes, getsibling, combo_scroll, type_text, press_key
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, datetime_tr

_local_path = '/installation/hub/datetime'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

# ignore for the moment
"""
# ugly hack copied from anaconda code
ETC_ZONES = ['GMT+1', 'GMT+2', 'GMT+3', 'GMT+4', 'GMT+5', 'GMT+6', 'GMT+7',
             'GMT+8', 'GMT+9', 'GMT+10', 'GMT+11', 'GMT+12',
             'GMT-1', 'GMT-2', 'GMT-3', 'GMT-4', 'GMT-5', 'GMT-6', 'GMT-7',
             'GMT-8', 'GMT-9', 'GMT-10', 'GMT-11', 'GMT-12', 'GMT-13',
             'GMT-14', 'UTC', 'GMT']

def all_timezones():
    result = {}
    for zone in pytz.common_timezones:
        try:
            region, city = zone.split("/", 1)
        except ValueError:
            continue
        try:
            result[region].append(city)
        except KeyError:
            result[region] = [city]
    result["Etc"] = ETC_ZONES
    return result

def all_regions():
    return all_timezones().keys()
"""

@handle_act('')
def base_handler(element, app_node, local_node):
    datetime_label = tr("DATE & TIME")
    datetime = getnode_scroll(app_node, "spoke selector", datetime_label)
    datetime.click()
    datetime_panel = getnode(app_node, "panel", tr("DATE & TIME"))
    default_handler(element, app_node, datetime_panel)
    done_button = getnode(datetime_panel, "push button", tr("_Done", False))
    done_button.click()

@handle_chck('')
def base_check(element, app_node, local_node):
    try:
        getnode(app_node, "panel", tr("DATE & TIME"), visible=False)
        return True
    except TimeoutError:
        return (False, "Datetime spoke is still visible.")

@handle_act('/region')
def region_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    region_name = datetime_tr(value)
    region_label = getnode(local_node, "label",
                           tr("_Region:", context="GUI|Date and Time"))
    region_combo = getsibling(region_label, 1, "combo box")
    # can't do this better (simple) way
    region_combo.actions['press'].do()
    combo_window = getnode(app_node, "window")
    region_item = getnode(combo_window, "menu item", region_name)
    region_item.click()

@handle_chck('/region')
def region_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # I don't know why, but the region is not translated in name of widget
    #region_name = datetime_tr(value)
    region_name = value
    region_label = getnode(local_node, "label",
                           tr("_Region:", context="GUI|Date and Time"))
    region_combo = getsibling(region_label, 1, "combo box")
    return unicode(region_combo.name) == unicode(region_name)

@handle_act('/city')
def city_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    city_name = datetime_tr(value)
    city_label = getnode(local_node, "label",
                         tr("_City:", context="GUI|Date and Time"))
    city_combo = getsibling(city_label, 1, "combo box")
    # can't do this better (simple) way
    city_combo.actions['press'].do()
    combo_window = getnode(app_node, "window")
    city_item = getnode(combo_window, "menu item", city_name)
    combo_scroll(city_item)
    city_item.click()

@handle_chck('/city')
def city_check(element, app_node, local_node):
    value = get_attr(element, "value")
    # I don't know why, but the city is not translated in name of widget
    #city_name = datetime_tr(value)
    city_name = value
    city_label = getnode(local_node, "label",
                         tr("_City:", context="GUI|Date and Time"))
    city_combo = getsibling(city_label, 1, "combo box")
    return unicode(city_combo.name) == unicode(city_name)

@handle_act('/ntp')
def ntp_handler(element, app_node, local_node):
    enable = get_attr(element, "value") == "enable"
    ntp_toggle = getnode(local_node, "toggle button", tr("Use Network Time"))
    if ntp_toggle.checked != enable:
        ntp_toggle.click()

@handle_chck('/ntp')
def ntp_check(element, app_node, local_node):
    enable = get_attr(element, "value") == "enable"
    ntp_toggle = getnode(local_node, "toggle button", tr("Use Network Time"))
    if ntp_toggle.checked != enable:
        return (False, "")
    return True

@handle_act('/ntp_settings')
def ntp_settings_handler(element, app_node, local_node):
    dialog_action = get_attr(element, 'dialog', 'accept')
    if dialog_action == 'accept':
        button_name = tr('_OK', context="GUI|Date and Time|NTP")
    elif dialog_action == 'dialog':
        button_name = tr('_Cancel', context="GUI|Date and Time|NTP")
    ntp_button = getnode(local_node, "push button", tr("Configure NTP"))
    ntp_button.click()
    local_node = getnode(app_node, "dialog", tr("Configure NTP"))
    default_handler(element, app_node, local_node)
    tmp_filler = getnode(local_node, 'filler', recursive=False)
    buttons_filler = getnodes(tmp_filler, 'filler', recursive=False)[-1]
    dialog_button = getnode(buttons_filler, "push button", button_name)
    dialog_button.click()

@handle_chck('/ntp_settings')
def ntp_settings_check(element, app_node, local_node):
    # TODO
    pass

@handle_act('/ntp_settings/add')
def ntp_settings_add_handler(element, app_node, local_node):
    hostname = get_attr(element, "hostname")
    input_node = getnode(local_node, "text", tr("New NTP Server"))
    input_node.click()
    input_node.typeText(hostname)
    add_button = getnode(local_node, "push button", tr("Add NTP Server"))
    add_button.click()

@handle_chck('/ntp_settings/add')
def ntp_settings_add_check(element, app_node, local_node):
    hostname = unicode(get_attr(element, "hostname"))
    table = getnode(local_node, "table")
    for candidate in getnodes(table, "table cell")[::3]:
        if fnmatch.fnmatchcase(unicode(candidate.name), hostname):
            return True
    return (False, "Specified ntp server not found")

@handle_act('/ntp_settings/rename')
def ntp_settings_rename_handler(element, app_node, local_node):
    old = get_attr(element, "old")
    new = get_attr(element, "new")
    table = getnode(local_node, "table")
    try:
        node = getnode(table, "table cell", old)
    except TimeoutError:
        return (False, "Specified ntp server not found")
    node.doubleClick()
    type_text(new)
    press_key('enter')
    return True

@handle_chck('/ntp_settings/rename')
def ntp_settings_rename_check(element, app_node, local_node):
    if action_result(element)[0] == False:
        return action_result(element)
    new = get_attr(element, "new")
    table = getnode(local_node, "table")
    try:
        node = getnode(table, "table cell", new)
        return True
    except TimeoutError:
        return (False, "Renamed ntp server not found")

def ntp_settings_enable_manipulate(element, app_node, local_node, enable, dry_run):
    hostname = get_attr(element, "hostname")
    table = getnode(local_node, "table")
    ok = True
    for candidate in getnodes(table, "table cell")[::3]:
        if fnmatch.fnmatchcase(unicode(candidate.name), hostname):
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
    return ntp_settings_enable_manipulate(element, app_node, local_node, True, True)

@handle_act('/ntp_settings/disable')
def ntp_settings_disable_handler(element, app_node, local_node):
    ntp_settings_enable_manipulate(element, app_node, local_node, False, False)

@handle_chck('/ntp_settings/disable')
def ntp_settings_disable_check(element, app_node, local_node):
    return ntp_settings_enable_manipulate(element, app_node, local_node, False, True)

@handle_act('/time')
def time_handler(element, app_node, local_node):
    datetime_node = getnode(local_node, "filler", tr("Set Date & Time"))
    time_node = getnode(datetime_node, "panel")
    default_handler(element, app_node, time_node)

@handle_chck('/time')
def time_check(element, app_node, local_node):
    pass

@handle_act('/time/hours')
def time_hours_handler(element, app_node, local_node):
    value = int(get_attr(element, "value"))
    hours_label = getnode(local_node, "label", tr("Hours"))
    hours_minus = getnode(local_node, "push button", tr("Hour Down"))
    hours_plus = getnode(local_node, "push button", tr("Hour Up"))
    for i in xrange(int(hours_label.text), value):
        hours_plus.click()
    for i in xrange(int(hours_label.text), value, -1):
        hours_minus.click()

@handle_chck('/time/hours')
def time_hours_check(element, app_node, local_node):
    value = get_attr(element, "value")
    hours_label = getnode(local_node, "label", tr("Hours"))
    if hours_label.text == value:
        return True
    return (False, "Hour didn't match desired value")

@handle_act('/time/minutes')
def time_minutes_handler(element, app_node, local_node):
    value = int(get_attr(element, "value"))
    minutes_label = getnode(local_node, "label", tr("Minutes"))
    minutes_minus = getnode(local_node, "push button", tr("Minutes Down"))
    minutes_plus = getnode(local_node, "push button", tr("Minutes Up"))
    for i in xrange(int(minutes_label.text), value):
        minutes_plus.click()
    for i in xrange(int(minutes_label.text), value, -1):
        minutes_minus.click()

@handle_chck('/time/minutes')
def time_minutes_check(element, app_node, local_node):
    value = get_attr(element, "value")
    minutes_label = getnode(local_node, "label", tr("Minutes"))
    if minutes_label.text == value:
        return True
    return (False, "Minute didn't match desired value")

def time_format_manipulate(element, app_node, local_node, dry_run):
    value = get_attr(element, "value")
    local_node = getsibling(local_node, 1, "panel")
    if value == "12":
        wanted_text = tr("24-_hour", context="GUI|Date and Time")
    elif value == "24":
        wanted_text = tr("_AM/PM", context="GUI|Date and Time")
    wanted_radio = getnode(local_node, "radio button", wanted_text)
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
    return time_format_manipulate(element, app_node, local_node, True)

@handle_act('/time/ampm')
def time_ampm_handler(element, app_node, local_node):
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
        return (False, "Didn't find neither AM, nor PM label")
    buttons = getnodes(local_node, "push button", tr("AM/PM Up"))
    buttons += getnodes(local_node, "push button", tr("AM/PM Down"))
    random_button = random.choice(buttons)
    if unicode(value) != unicode(ampm_label.text):
        random_button.click()
    return True

@handle_chck('/time/ampm')
def time_ampm_check(element, app_node, local_node):
    value = tr(get_attr(element, "value"))
    try:
        ampm_label = getnode(local_node, "label", value)
        return True
    except TimeoutError:
        return (False, "Didn't find correct label for '%s'" % value)

@handle_act('/date')
def date_handler(element, app_node, local_node):
    def date_combo_cmp(x, y):
        return cmp(len(getnodes(x, "menu item", visible=None)),
                   len(getnodes(y, "menu item", visible=None)))
    datetime_node = getnode(local_node, "filler", tr("Set Date & Time"))
    combos = sorted(getnodes(datetime_node, "combo box"), date_combo_cmp)
    date_panel = getnodes(datetime_node, "panel", recursive=False)[2]
    default_handler(element, app_node, combos)

@handle_chck('/date')
def date_check(element, app_node, local_node):
    pass

@handle_act('/date/month')
def date_month_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    month_combo = local_node[0]
    month_combo.click()
    window = getnode(app_node, "window")
    item = getnode(window, "menu item", value)
    combo_scroll(item)
    item.click()

@handle_chck('/date/month')
def date_month_check(element, app_node, local_node):
    value = get_attr(element, "value")
    month_combo = local_node[0]
    pass

@handle_act('/date/day')
def date_day_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    day_combo = local_node[1]
    pass

@handle_chck('/date/day')
def date_day_check(element, app_node, local_node):
    value = get_attr(element, "value")
    day_combo = local_node[1]
    pass

@handle_act('/date/year')
def date_year_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    year_combo = local_node[2]
    pass

@handle_chck('/date/year')
def date_year_check(element, app_node, local_node):
    value = get_attr(element, "value")
    year_combo = local_node[2]
    pass
