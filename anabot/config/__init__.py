import logging
from ConfigParser import RawConfigParser
from anabot.paths  import defauls_path, profiles_path

_profile_name = None
_config = None


# log_level translating
_log_levels = {
    None: logging.NOTSET,
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}

_empty_meanings = {
    'chroot': None,
    'atk_min_children': 0,
}

replacements = {
    'profile_name': None,
}

def init_config(profile_name):
    global _profile_name
    global _config

    ini_path = profiles_path + '/' + profile_name + '.ini'
    _config = RawConfigParser(allow_no_value=True)
    defaults = open(defauls_path, 'r')
    _config.readfp(defaults)
    loaded = _config.read(ini_path)
    if not ini_path in loaded:
        raise Exception("Cannot load '%s'" % ini_path)
    _profile_name = profile_name
    replacements['profile_name'] = profile_name

def get_option(option):
    if option == 'log_level':
        return _log_levels[_config.get(_profile_name, option)]
    if option == 'profile_name':
        return _profile_name
    value = _config.get(_profile_name, option) % replacements
    if value == "":
        if _empty_meanings.has_key(option):
            value = _empty_meanings[option]
    return value

