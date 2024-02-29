import logging
logger = logging.getLogger('anabot')

import functools
import operator
import platform
import re
import os
from subprocess import Popen, PIPE
from time import sleep
from distutils.version import LooseVersion

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

def _anaconda_version():
    # Determine anaconda version, env ANACONDA_VERSION > anaconda.log > rpm
    try:
        return os.environ['ANACONDA_VERSION']
    except KeyError:
        logger.debug('Cannot get anaconda version from ANACONDA_VERSION variable')

    try:
        with open('/root/lorax-packages.log') as lorax_packages_log:
            match = re.search(r'^(anaconda)-([0-9]+(\.[0-9]+)*)',
                              lorax_packages_log.read(),
                              re.MULTILINE)
            version = match.group(2)
            logger.debug('Determined anaconda version from lorax-packages.log: %s' % version)
            return version
    except (IOError, AttributeError):
            logger.debug('Anaconda version not found in lorax-packages.log')
    logger.debug('Cannot determine anaconda version from lorax-packages.log')

    try:
        output = Popen(['rpm', '-q', '--qf', '%{VERSION}', 'anaconda'], stdout=PIPE)
        response = output.communicate()
        if output.returncode == 0:
            return response[0].decode('utf-8')
        else:
            raise RuntimeError(response)
    except RuntimeError as e:
        logger.debug('Cannot determine anaconda version from rpm')
        logger.debug(e)

    logger.error('Could not determine anaconda version')

_cache['distro'] = _distro()
_cache['anaconda_version'] = _anaconda_version()

def distro():
    return _cache['distro']

def anaconda_version():
    return _cache['anaconda_version']

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

def is_distro_version_lt(name, major, minor=None):
    return is_distro_version_op(operator.lt, name, major, minor)

def is_distro_version_le(name, major, minor=None):
    return is_distro_version_op(operator.le, name, major, minor)

def is_anaconda_version_op(op, version):
    if anaconda_version():
        return op(LooseVersion(anaconda_version()), LooseVersion(version))
    else:
        return False

def is_anaconda_version(version):
     return is_anaconda_version_op(operator.eq, version)

def is_anaconda_version_ge(version):
    return is_anaconda_version_op(operator.ge, version)

def is_anaconda_version_gt(version):
    return is_anaconda_version_op(operator.gt, version)

def is_anaconda_version_le(version):
    return is_anaconda_version_op(operator.le, version)

def is_anaconda_version_lt(version):
    return is_anaconda_version_op(operator.lt, version)

def has_feature_hub_config():
    # Fedora https://github.com/rhinstaller/anaconda/commit/b2adda24ea8233cff6e0afd0a48c475a801fe3b4
    if is_distro('fedora') and is_anaconda_version_ge('31.20.1'):
        return True
    # RHEL - information from rvykydal and first nightly compose with this feature
    if is_distro('rhel') and is_anaconda_version_ge('33.16.3'):
        return True
    return False

def is_liveimg_install():
    if os.path.exists('/run/install/ks.cfg'):
        with open('/run/install/ks.cfg', 'r') as ks:
            for line in ks.readlines():
                if re.search(r"\s*liveimg.*\s+--url", line):
                    return True
    return False

