.. Anabot documentation master file, created by
   sphinx-quickstart on Thu Feb 25 11:47:17 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
Welcome to Anabot's documentation!
==================================

.. warning::

    Some parts of this documentation are outdated!

About Anabot
============

Anabot is engine for automated GUI testing. It's takes XML recipe (data) as
input and performs actions and checks (code) specified in the recipe. It's
focused on abstracting instructions from the actual code, so that anybody
can easily run it's own recipe without the need of knowing anything about e.g.
dogtail.

There's also other advantage to this model. Since XML is used, it's possible
to use all the tooling developed around it. It's possible to validate the XML
before actually trying to use it. It's possible to have XSLT adding some
actions to the recipe etc.

What is anabot for
------------------

Anabot is for GUI testing. It interacts with the GUI application and checks
that desired/expected effects occur. It can also be used as a way to just
control some GUI application when there is no CLI alternative, and in that
case, it has added value of checking the GUI process itself.

What is anabot not for
----------------------

Performing tasks that could be done different way. If the GUI is not explicitly
required, anabot adds unnecessary complexity.

========
Contents
========

.. toctree::
   :maxdepth: 2

   101
   workflow
   external_variables
   decorators
   history
   debugging


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

