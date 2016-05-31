# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('anabot')

from fnmatch import fnmatchcase

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler, action_result
from anabot.runtime.functions import get_attr, getnode, getnodes, getnode_scroll, scrollto
from anabot.runtime.errors import TimeoutError
from anabot.runtime.translate import tr

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

@handle_chck('')
def base_check(element, app_node, local_node):
    try:
        getnode(app_node, "panel", tr("DATE & TIME"), visible=False)
        return True
    except TimeoutError:
        return (False, "Datetime spoke is still visible.")

@handle_act('/region')
def region_handler(element, app_node, local_node):
    pass

@handle_chck('/region')
def region_check(element, app_node, local_node):
    pass

@handle_act('/city')
def city_handler(element, app_node, local_node):
    pass

@handle_chck('/city')
def city_check(element, app_node, local_node):
    pass

@handle_act('/ntp')
def ntp_handler(element, app_node, local_node):
    pass

@handle_chck('/ntp')
def ntp_check(element, app_node, local_node):
    pass

@handle_act('/ntp_settings')
def ntp_settings_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/ntp_settings')
def ntp_settings_check(element, app_node, local_node):
    pass

@handle_act('/ntp_settings/server')
def ntp_settings_server_handler(element, app_node, local_node):
    pass

@handle_chck('/ntp_settings/server')
def ntp_settings_server_check(element, app_node, local_node):
    pass

@handle_act('/time')
def time_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/time')
def time_check(element, app_node, local_node):
    pass

@handle_act('/time/hours')
def time_hours_handler(element, app_node, local_node):
    pass

@handle_chck('/time/hours')
def time_hours_check(element, app_node, local_node):
    pass

@handle_act('/time/minutes')
def time_minutes_handler(element, app_node, local_node):
    pass

@handle_chck('/time/minutes')
def time_minutes_check(element, app_node, local_node):
    pass

@handle_act('/time/format')
def time_format_handler(element, app_node, local_node):
    pass

@handle_chck('/time/format')
def time_format_check(element, app_node, local_node):
    pass

@handle_act('/time/ampm')
def time_ampm_handler(element, app_node, local_node):
    pass

@handle_chck('/time/ampm')
def time_ampm_check(element, app_node, local_node):
    pass

@handle_act('/date')
def date_handler(element, app_node, local_node):
    default_handler(element, app_node, local_node)

@handle_chck('/date')
def date_check(element, app_node, local_node):
    pass

@handle_act('/date/month')
def date_month_handler(element, app_node, local_node):
    pass

@handle_chck('/date/month')
def date_month_check(element, app_node, local_node):
    pass

@handle_act('/date/day')
def date_day_handler(element, app_node, local_node):
    pass

@handle_chck('/date/day')
def date_day_check(element, app_node, local_node):
    pass

@handle_act('/date/year')
def date_year_handler(element, app_node, local_node):
    pass

@handle_chck('/date/year')
def date_year_check(element, app_node, local_node):
    pass
