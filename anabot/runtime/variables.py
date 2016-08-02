__VARIABLES = {}

def set_variable(name, value):
    __VARIABLES[name] = value

def get_variable(name, default=None):
    return __VARIABLES.get(name, default)
