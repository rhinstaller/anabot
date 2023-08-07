===================
Installation Source
===================

/installation/hub/installation_source/additional_repo
=====================================================
Handles *Additional repositories*.

/installation/hub/installation_source/additional_repo/add
=========================================================
Adds an additional repository to the list.

Attributes:

* ``name``
* ``url``
* ``url_type`` - ``repo``, ``mirrorlist``, ``metalink``
* ``url_protocol`` - ``http://``, ``https://``, ``ftp://``, ``nfs``
* ``proxy_url``
* ``proxy_username``
* ``proxy_password``
* ``enabled`` - ``0|off|false`` or ``1|on|true``

/installation/hub/installation_source/additional_repo/infobar
=============================================================
Equivalent to `/installation/hub/installation_source/infobar`_.

/installation/hub/installation_source/additional_repo/reset
===========================================================
Reset the additional repositories to original state using the *Revert* button.

/installation/hub/installation_source/additional_repo/select
============================================================
Selects repositories matching a name (fnmatchcase expression) and repo status
and performs arbitrary changes on the selected set. Doesn't work with
``policy="just_check"`` or ``policy="just_check_fail"``, as it relies
on an existing action result in the check.

Attributes:

* ``name`` - repo name (fnmatchcase expression)
* ``enabled`` - ``0|off|false`` or ``1|on|true``

/installation/hub/installation_source/additional_repo/select/infobar
====================================================================
Equivalent to `/installation/hub/installation_source/infobar`_.

/installation/hub/installation_source/additional_repo/select/name
=================================================================
Set/check *name* of selected repo(s).

Attributes:

* ``value``

/installation/hub/installation_source/additional_repo/select/proxy_password
===========================================================================
Set/check proxy *password* of selected repo(s).

Attributes:

* ``value``

/installation/hub/installation_source/additional_repo/select/proxy_url
======================================================================
Set/check *Proxy URL* of selected repo(s).

Attributes:

* ``value``

/installation/hub/installation_source/additional_repo/select/proxy_username
===========================================================================
Set/check proxy *user name* of selected repo(s).

Attributes:

* ``value``

/installation/hub/installation_source/additional_repo/select/remove
===================================================================
Remove selected repo(s).

/installation/hub/installation_source/additional_repo/select/status
===================================================================
Enables or disables selected repo(s).

Attributes:

* ``enabled`` - ``0|off|false`` or ``1|on|true``

/installation/hub/installation_source/additional_repo/select/url
================================================================
Sets URL for selected repo(s).

Attributes:

* ``value``

/installation/hub/installation_source/additional_repo/select/url_protocol
=========================================================================
Sets URL protocol for selected repo(s).

Attributes:

* ``value``

/installation/hub/installation_source/additional_repo/select/url_type
=====================================================================
Sets URL type for selected repo(s).

Attributes:

* ``value`` - ``http://``, ``https://``, ``ftp://``, ``nfs``

/installation/hub/installation_source/choose_iso
================================================
*Choose an ISO* dialog. **Not implemented at this point.**

/installation/hub/installation_source/infobar
=============================================
Check presence of info bar at the bottom of the screen and displayed message

Attributes:

* ``message`` - expected message; if ``*`` is used, only presence of info bar is checked
* ``repo_name`` (optional) - repo name that will be put into the message after translation

/installation/hub/installation_source/iso_device
================================================
*Device* combo box for ISO file. **Not implemented at this point.**

/installation/hub/installation_source/main_repo_type
====================================================
Main repo *URL type* combo box.

Attributes:

* ``value`` - ``repo``, ``mirrorlist``, ``metalink``

/installation/hub/installation_source/main_repo_url
===================================================
Main repo (*On the network* source) URL.

Attributes:

* ``value``

/installation/hub/installation_source/main_repo_url_protocol
============================================================
Main repo (*On the network* source) URL protocol.

Attributes:

* ``value``

/installation/hub/installation_source/proxy
===========================================
Handles installation source proxy setup dialog.

/installation/hub/installation_source/proxy/authentication
==========================================================
*Use Authentication* check box.

Attributes:

* ``enable`` - ``0|off|false`` or ``1|on|true``

/installation/hub/installation_source/proxy/cancel
==================================================
Cancels the proxy setup dialog.

/installation/hub/installation_source/proxy/host
================================================
*Proxy Host* input field.

Attributes:

* ``value``

/installation/hub/installation_source/proxy/ok
==============================================
Confirms the settings in the proxy setup dialog.

/installation/hub/installation_source/proxy/password
====================================================
Proxy *password* input field.

Attributes:

* ``value``

/installation/hub/installation_source/proxy/status
==================================================
*Enable HTTP Proxy* check box.

Attributes:

* ``enable`` - ``0|off|false`` or ``1|on|true``

/installation/hub/installation_source/proxy/username
====================================================
*User name* input field.

Attributes:

* ``value``

/installation/hub/installation_source/source
============================================
Installation source (radio button group) selection.

Attributes:

* ``type`` - ``media`` (*Auto-detected installation media*), ``cdn`` (*Red Hat CDN*),
  ``iso`` (*ISO file*), ``network`` (*On the network*)

/installation/hub/installation_source/verify_iso
================================================
Handles ISO verification (dialog). **Not implemented at this point**

/installation/hub/installation_source/verify_media
==================================================
Handles verification of the auto-detected installation medium.
