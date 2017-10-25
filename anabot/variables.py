import os
import six

__VARIABLES = {}
__ENV_PREFIX = 'ANABOT_VAR_'

def set_variable(name, value):
    if not isinstance(value, six.string_types):
        raise TypeError("Only 'str' and 'unicode', %s given" % type(value))
    __VARIABLES[name] = value
    set_env_variable(__ENV_PREFIX + name.upper(), value)

def get_variable(name, default=None):
    return __VARIABLES.get(name, default)

def get_variables():
    return __VARIABLES.copy()

set_env_variable = os.environ.__setitem__
