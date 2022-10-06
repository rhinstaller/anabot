Decorators
==========

.. py:function:: handle_action(element_path[, func=None])

    Decorator for handler function.

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

.. py:function:: handle_check(element_path[, func=None])

    Decorator for checker function.

    This function is used to register check function *func* for XML element
    *element_path* in the same way as :py:func:`handle_action`.

.. py:function:: check_action_result(func)

    Decorator used for checker functions.

    This is shortcut for checkers to test if corresponding action failed.
    If that's the case, the decorated checker immediately ends returning
    result from corresponding action.

    This can be imagined as checker containing following code at the
    beginning::

        @handle_check("/installation/welcome")
        def welcome_check(element, app_node, local_node):
            if action_result(element) == False:
                return action_result(element)
            # code of the check

    Equivalent using :py:func:`check_action_result`::

        @handle_check("/installation/welcome")
        @check_action_result
        def welcome_check(element, app_node, local_node):
            # code of the check
