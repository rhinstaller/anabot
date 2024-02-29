===================
Root Password spoke
===================

/installation/configuration/root_password
=========================================
Equivalent to :ref:`recipe_elements/hub:/installation/hub/root_password`.

/installation/configuration/root_password/confirm_password
==========================================================
Equivalent to `/installation/hub/root_password/confirm_password`_.

/installation/configuration/root_password/done
==============================================
Equivalent to `/installation/hub/root_password/done`_.

/installation/configuration/root_password/password
==================================================
Equivalent to `/installation/hub/root_password/password`_.

/installation/hub/root_password/root_account
========================================
Enable or disable the *Root account*. It was introduced in RHEL 10 and the new workflow demands the root account to be
enabled first before setting the root password.

Attributes:

* ``value`` - ``enable`` or ``disable`` (any other value will be considered as ``disable``)

/installation/hub/root_password/allow_root_ssh_login_with_password
==================================================================
*Allow root SSH login with password* check box.

Attributes:

* ``checked`` - ``yes`` or ``no``

/installation/hub/root_password/confirm_password
================================================
*Confirm* password input field.

Attributes:

* ``value``

/installation/hub/root_password/done
====================================
*Done* button.

/installation/hub/root_password/lock_root_account
=================================================
*Lock root account* check box.

Attributes:

* ``checked`` - ``yes`` or ``no``

/installation/hub/root_password/password
========================================
*Root Password* input field.

Attributes:

* ``value``
