ACTIONS = {}
CHECKS = {}

def handle_action(element_path):
    def tmp(func):
        ACTIONS[element_path] = func
        return func
    return tmp

def handle_check(element_path):
    def tmp(func):
        CHECKS[element_path] = func
        return func
    return tmp
