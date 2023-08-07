========================================
Configuration/Installation process spoke
========================================

/installation/configuration
===========================
Used for *configuration* spoke that appears during installation process and displays EULA
notice and Reboot button when installation is complete.

.. note::
    This element originally provided options to create a user and set root password.
    The elements for user/root configuration are internally equivalent to
    :ref:`recipe_elements/hub:/installation/hub/create_user` and
    :ref:`recipe_elements/hub:/installation/hub/root_password`.

/installation/configuration/eula_notice
=======================================
Checks presence of warning bar on the bottom of the screen containing a proper message
about EULA which appears when the installation is complete. It has only a check implemented
(no handler), thus has to be used with ``policy=just_check``.

/installation/configuration/finish_configuration
================================================
Handles button used for finishing configuration during installation process (RHEL-7 only).

/installation/configuration/reboot
==================================
Clicks *Reboot* button after installation is complete.

/installation/configuration/root
================================
A shortcut element usable only within the ``ez:`` namespace, functionally equivalent to
:ref:`recipe_elements/hub:/installation/hub/root`.

/installation/configuration/root_password
=========================================
Functionally equivalent to :ref:`recipe_elements/hub:/installation/hub/root_password`.

/installation/configuration/wait_until_complete
===============================================
A special element not used to directly handle any Anaconda's function, but to wait
until for the installation process to finish. It is a necessary part before
clicking on the Reboot button as the button is inactive during installation.

/installation/configuration/create_user/advanced
================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced`.

/installation/configuration/create_user/advanced/cancel
=======================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/cancel`.

/installation/configuration/create_user/advanced/gid
====================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/gid`.

/installation/configuration/create_user/advanced/groups
=======================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/groups`.

/installation/configuration/create_user/advanced/home
=====================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/home`.

/installation/configuration/create_user/advanced/manual_gid
===========================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/manual_gid`.

/installation/configuration/create_user/advanced/manual_uid
===========================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/manual_uid`.

/installation/configuration/create_user/advanced/save
=====================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/save`.

/installation/configuration/create_user/advanced/uid
====================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/advanced/uid`.

/installation/configuration/create_user/confirm_password
========================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/confirm_password`.

/installation/configuration/create_user/done
============================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/done`.

/installation/configuration/create_user/full_name
=================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/full_name`.

/installation/configuration/create_user/is_admin
================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/is_admin`.

/installation/configuration/create_user/password
================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/password`.

/installation/configuration/create_user/require_password
========================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/require_password`.

/installation/configuration/create_user/username
================================================
Equivalent to :ref:`recipe_elements/create_user:/installation/hub/create_user/username`.