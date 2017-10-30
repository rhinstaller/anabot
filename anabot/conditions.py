import logging
logger = logging.getLogger('anabot')

import functools
import operator
import platform

_cache = {}

def _distro():
    # platform.dist doesn't work in fedora installation image
    data = {}
    with open('/etc/os-release') as os_release:
        for line in os_release:
            line = line.rstrip('\n')
            logger.debug(line)
            try:
                key, value = line.split('=', 1)
            except ValueError:
                continue
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1] # drop first and last character
            logger.debug("key: %s", key)
            logger.debug("value: %s", value)
            data[key] = value
    version = data['VERSION_ID']
    try:
        major, minor = version.split('.', 1)
        major, minor = int(major), int(minor)
    except ValueError:
        major, minor = int(version), float('NaN')
    d = {
        'name' : data['ID'],
        'version' : version,
        'major' : major,
        'minor' : minor,
    }
    return d

_cache['distro'] = _distro()

def distro():
    return _cache['distro']

def is_distro(name):
    return name == distro()['name']

def is_distro_version_op(op, name, major, minor=None):
    if not (is_distro(name) and op(distro()['major'], major)):
        return False
    return minor is None or op(distro()['minor'], minor)

def is_distro_version(name, major, minor=None):
    return is_distro_version_op(operator.eq, name, major, minor)

def is_distro_version_gt(name, major, minor=None):
    return is_distro_version_op(operator.gt, name, major, minor)

def is_distro_version_ge(name, major, minor=None):
    return is_distro_version_op(operator.ge, name, major, minor)
