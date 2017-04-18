import os

__VARIABLES = {}
__ENV_PREFIX = 'ANABOT_VAR_'

def set_variable(name, value):
    if not isinstance(value, (str, unicode)):
        raise TypeError("Only 'str' and 'unicode', %s given" % type(value))
    __VARIABLES[name] = value
    os.environ[__ENV_PREFIX + name.upper()] = value

def get_variable(name, default=None):
    return __VARIABLES.get(name, default)

def get_variables():
    return __VARIABLES.copy()
