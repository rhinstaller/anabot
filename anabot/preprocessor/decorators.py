_REPLACES = {}
_DEFAULTS = {}

def replace(node_path):
    def decorator(func):
        _REPLACES[node_path] = func
        return func
    return decorator

def default(application, node_path):
    def decorator(func):
        _DEFAULTS[(application, node_path)] = func
        return func
    return decorator
