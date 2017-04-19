import os
from ConfigParser import RawConfigParser
from anabot.paths  import defauls_path, profiles_path

_profile_name = None
_config = None

_empty_meanings = {
    'chroot': None,
    'atk_min_children': 0,
    'log_level': 'NOTSET'
}

replacements = {
    'profile_name': None,
}

def init_config(profile_name):
    global _profile_name
    global _config

    ini_path = os.path.join(profiles_path, profile_name + '.ini')
    _config = RawConfigParser(allow_no_value=True)
    defaults = open(defauls_path, 'r')
    _config.readfp(defaults)
    loaded = _config.read(ini_path)
    if not ini_path in loaded:
        raise Exception("Cannot load '%s'" % ini_path)
    _profile_name = profile_name
    replacements['profile_name'] = profile_name

def get_option(option):
    value = _config.get(_profile_name, option) % replacements
    if value == "":
        value = _empty_meanings.get(option, value)
    return value

