==================
External variables
==================

It is possible to pass external variables to Anabot, using either
kernel command line or Beaker task parameters. The main use
of externally defined variables is for enhancing recipes, where
a variable placeholder can be substituted by Anabot's preprocessor,
thus providing a greater flexibility in comparison with just static
recipes.

.. note::
    Even though the main reason for introducing external variables
    is their use in recipes, it is technically possible to use
    those variables generally in Anabot's code, since those variables
    are internally handled by |get_variable|_ and |set_variable|_.

    .. |get_variable| replace:: ``get_variable()``
    .. _get_variable: https://github.com/rhinstaller/anabot/blob/main/anabot/variables.py
    .. |set_variable| replace:: ``set_variable()``
    .. _set_variable: https://github.com/rhinstaller/anabot/blob/main/anabot/variables.py

.. warning::
    When defining external variables, chooose their names wisely.
    As mentioned in the note above, they occupy the shared internal
    variables space, which will lead to a clash when another variable with
    the same name is used elsewhere in Anabot's code, leading to
    undefined behaviour.

    A list of already existing variables in Anabot code using this
    mechanism can be obtained for instance by running the following command:
    in Anabot repository:
    ``git grep -Pho "(get|set)_variable\([\"']\K[^'\"]+" | sort -u``

.. warning::
    If a variable is defined both on kernel command line and in Beaker
    task parameter, the command line one takes precedence. However, it is best
    to avoid defining the same variable using both mechanisms at the same time.

Kernel command line
===================
It is possible to define an external variable on kernel command line using
``anabot.variable_name=variable_value`` or ``anabot.variable_name="variable value"``.
The ``anabot.`` prefix will be removed and a variable named ``variable_name``
with value ``variable_value`` (or ``variable value`` respectively) will be defined.

Beaker task parameters
======================
Another option to pass the variables is to use Beaker task parameters.
The parameters use ``ANABOT_SUB_`` prefix, which is removed and the rest
of variable name is converted to lowercase.

For example, ``<param name="ANABOT_SUB_LANG" value="Czech">`` will translate
into a variable named ``lang`` with value ``Czech``.

Use in recipes
==============
Variable placeholders in recipes are substituted by external variables passed
to Anabot by means of Python string template formatting (``str.format()``)
in conjunction with a dedicated ``<ez:sub/>`` element. This element handles
a substitution for an element specified by its ``ez:name`` attribute.

.. note::
    It's necessary to use the ``sub`` element with the ``ez`` namespace specified,
    otherwise it won't be recognized and Anabot will end up with an error.
    The same notice is valid for the ``name`` attribute.

It is strongly advised to use only **lowercase** placeholder names, since variable
names originating from Beaker parameters always get converted to lowercase.

For example, ``<ez:sub ez:name="language" value="{lang}" />`` in the recipe with the
``lang`` variable set to ``Czech`` (defined by ``anabot.lang`` on kernel command
line or ``ANABOT_SUB_LANG`` Beaker task parameter) will get substituted for 
``<language value="Czech" />``.

