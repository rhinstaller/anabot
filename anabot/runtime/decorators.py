import logging
logger = logging.getLogger('anabot')

from functools import wraps
from .default import action_result

ACTIONS = {}
CHECKS = {}

def handle_action(element_path, func=None):
    """Decorator for handler function.

    As a decorator this function is used to register handler functuon for XML
    element *element_path* located at element_path (e.g. /installation/welcome).
    Use only absolute paths without wildcards or any other special features.

    It can be used also as an ordinary function with function *func* as an
    argument.

    As decorator::

        @handle_action("/installation/welcome")
        def welcome_handler(element, app_node, local_node):

    As function::

        handle_action("/installation/welcome", welcome_handler)
    """
    def decorator(func):
        logger.debug("Registering handler for path: %s", element_path)
        ACTIONS[element_path] = func
        return func
    if func is not None:
        return decorator(func)
    return decorator

def handle_check(element_path, func=None):
    """Decorator for checker function.

    This function is used to register check function *func* for XML element
    *element_path* in the same way as :py:func:`handle_action`.
    """
    def decorator(func):
        CHECKS[element_path] = func
        return func
    if func is not None:
        return decorator(func)
    return decorator

def check_action_result(func):
    @wraps(func)
    def wrapper(element, app_node, local_node):
        if action_result(element) == False:
            return action_result(element)
        return func(element, app_node, local_node)
    return wrapper
