import logging
logger = logging.getLogger('anabot')

_REPLACES = {}
_DEFAULTS = {}

def replace(node_path, cond=True):
    def decorator(func):
        if cond:
            logger.debug("Replacing path: %s", node_path)
            _REPLACES[node_path] = func
        else:
            logger.debug("Skipping replacement of path: %s", node_path)
        return func
    return decorator

def default(application, node_path):
    def decorator(func):
        _DEFAULTS[(application, node_path)] = func
        return func
    return decorator
