ACTIONS = {}
CHECKS = {}

def handle_action(element_path, func=None):
    def decorator(func):
        ACTIONS[element_path] = func
        return func
    if func is not None:
        return decorator(func)
    return decorator

def handle_check(element_path, func=None):
    def decorator(func):
        CHECKS[element_path] = func
        return func
    if func is not None:
        return decorator(func)
    return decorator
