# -*- coding: utf-8 -*-

class UnrelatedException(Exception):
    """
    Unrelated exception is used by anabot modules in their __init__.py.
    When such module raises this exception, it indicates, that it doesn't
    make sense to use this module in current environment; it's silently
    ignored by anabot.
    """
    pass
