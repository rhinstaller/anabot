# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnode_scroll, getsibling, combo_scroll
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr, datetime_tr

_local_path = '/installation/hub/datetime'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)

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
    action = get_attr(element, "value")
    pass

@handle_chck('/ntp')
def ntp_check(element, app_node, local_node):
    action = get_attr(element, "value")
    pass

@handle_act('/ntp_settings')
def ntp_settings_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/ntp_settings')
def ntp_settings_check(element, app_node, local_node):
    pass

@handle_act('/ntp_settings/server')
def ntp_settings_server_handler(element, app_node, local_node):
    hostname = get_attr(element, "hostname")
    pass

@handle_chck('/ntp_settings/server')
def ntp_settings_server_check(element, app_node, local_node):
    hostname = get_attr(element, "hostname")
    pass

@handle_act('/time')
def time_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/time')
def time_check(element, app_node, local_node):
    pass

@handle_act('/time/hours')
def time_hours_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/time/hours')
def time_hours_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_act('/time/minutes')
def time_minutes_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/time/minutes')
def time_minutes_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_act('/time/format')
def time_format_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/time/format')
def time_format_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_act('/time/ampm')
def time_ampm_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/time/ampm')
def time_ampm_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_act('/date')
def date_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/date')
def date_check(element, app_node, local_node):
    pass

@handle_act('/date/month')
def date_month_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/date/month')
def date_month_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_act('/date/day')
def date_day_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/date/day')
def date_day_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_act('/date/year')
def date_year_handler(element, app_node, local_node):
    value = get_attr(element, "value")
    pass

@handle_chck('/date/year')
def date_year_check(element, app_node, local_node):
    value = get_attr(element, "value")
    pass
