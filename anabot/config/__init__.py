import os

try: # python3
    from configparser import RawConfigParser
except ImportError: # python2
    from ConfigParser import RawConfigParser
from anabot.paths  import defauls_path, profiles_path
from anabot.variables import set_variable

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
    try:
        local_conf_path = os.environ.get(
            'ANABOT_CONF', os.path.join(os.getcwd(), 'anabot.ini')
        )
        with open(local_conf_path) as local_conf:
            _config.readfp(local_conf)
    except OSError:
        # couldn't find or read 'anabot.ini'
        pass
    loaded = _config.read(ini_path)
    if not ini_path in loaded:
        raise Exception("Cannot load '%s'" % ini_path)
    _profile_name = profile_name
    replacements['profile_name'] = profile_name
    # Set variables defined by the config file
    for option in _config.options(profile_name):
        if not option.startswith("var_"):
            continue
        # remove starting "var_"
        env_name = option.split('_', 1)[1]
        set_variable(env_name, get_option(option))

def get_option(option):
    value = _config.get(_profile_name, option) % replacements
    if value == "":
        value = _empty_meanings.get(option, value)
    return value

