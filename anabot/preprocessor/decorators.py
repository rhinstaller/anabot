import logging
logger = logging.getLogger('anabot')

_REPLACES = {}

def replace(node_path, cond=True):
    def decorator(func):
        if cond:
            logger.debug("Replacing path: %s", node_path)
            _REPLACES[node_path] = func
        else:
            logger.debug("Skipping replacement of path: %s", node_path)
        return func
    return decorator
