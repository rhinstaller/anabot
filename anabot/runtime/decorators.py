import logging
logger = logging.getLogger('anabot')

from functools import wraps, partial
from .handlers import ACTIONS, CHECKS
from .results import action_result

def handle_action(element_path, func=None, cond=True, prefix=None):
    """Decorator for handler function.

    As a decorator this function is used to register handler functuon for XML
    element *element_path* located at element_path (e.g. /installation/welcome).
    Use only absolute paths without wildcards or any other special features.

    It can be used also as an ordinary function with function *func* as an
    argument.

    Optional argument cond can be passed. If True (default), the handler will
    be registered. This is useful when deciding if the handler should be used
    e.g. on RHEL-7, Fedora or other environment condition.

    As decorator::

        @handle_action("/installation/welcome")
        def welcome_handler(element, app_node, local_node):

    Creating decorator shortcut::

        handle_act = functools.partial(handle_action, prefix="/installation")
        @handle_act("/welcome")
        def welcome_handler(element, app_node, local_node):

    As function::

        handle_action("/installation/welcome", welcome_handler)
    """
    if prefix is not None:
        element_path = prefix + element_path
    def decorator(func):
        if cond:
            logger.debug("Registering handler for path: %s", element_path)
            ACTIONS[element_path] = func
        else:
            logger.debug(
                "Skipping handler registration for path: %s",
                element_path
            )
        return func
    if func is not None:
        return decorator(func)
    return decorator

def make_prefixed_handle_action(prefix):
    return partial(handle_action, prefix=prefix)

def handle_check(element_path, func=None, cond=True, prefix=None):
    """Decorator for checker function.

    This function is used to register check function *func* for XML element
    *element_path* in the same way as :py:func:`handle_action`.
    """
    if prefix is not None:
        element_path = prefix + element_path
    def decorator(func):
        if cond:
            logger.debug("Registering check for path: %s", element_path)
            CHECKS[element_path] = func
        else:
            logger.debug(
                "Skipping check registration for path: %s",
                element_path
            )
        return func
    if func is not None:
        return decorator(func)
    return decorator

def make_prefixed_handle_check(prefix):
    return partial(handle_check, prefix=prefix)

def check_action_result(func):
    @wraps(func)
    def wrapper(element, app_node, local_node):
        if action_result(element) == False:
            return action_result(element)
        return func(element, app_node, local_node)
    return wrapper
