ACTIONS = {}
CHECKS = {}

def handle_action(element_path, func=None):
    """Decorator for handler function

    This function is used to register callback function for XML element
    located at element_path (e.g. /installation/welcome). Use only absolute
    paths without wildcards or any other special features.

    arguments:
    element_path -- path to XML node

    Keyword argumenst:
    func -- (default None)

    This function can be used either as decorator:
    @handle_action("/installation/welcome")
    def welcome_handler(element, app_node, local_node):
    ...

    Or as function where the registered function is passed as argument:
    handle_action("/installation/welcome", welcome_handler)
    """
    def decorator(func):
        ACTIONS[element_path] = func
        return func
    if func is not None:
        return decorator(func)
    return decorator

def handle_check(element_path, func=None):
    """Decorator for checker function

    This function is used to register check function same way as handle_action.

    arguments:
    element_path -- path to XML node

    Keyword argumenst:
    func -- (default None)
    """
    def decorator(func):
        CHECKS[element_path] = func
        return func
    if func is not None:
        return decorator(func)
    return decorator
