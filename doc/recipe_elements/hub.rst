==============================
Installation Hub (main screen)
==============================

/installation/hub
=================
Handles main Anaconda hub (main screen with buttons for configuration of various areas - *spokes*), takes no attributes.

/installation/hub/autopart
==========================
Shortcut element encompassing the following steps necessary to complete automatic partitioning:

* Enter *Installation Destination* spoke,
* select all available standard and specialized disks,
* opt to reclaim additional space,
* remove all available partitions in the reclaim dialog,
* confirm the configuration.

/installation/hub/begin_installation
====================================
Clicks on *Begin installation* button.

/installation/hub/connect_to_redhat
===================================
Handles :doc:`Connect to Red Hat <connect_to_redhat>` spoke.

/installation/hub/create_user
=============================
Handles :doc:`User Creation <create_user>` spoke.

/installation/hub/datetime
==========================
Handles :doc:`Time & Date <datetime>` spoke.

/installation/hub/installation_source
=====================================
Handles :doc:`Installation Source <installation_source>` spoke.

/installation/hub/kdump
=======================
Handles *KDUMP* spoke. Only **entering/exiting** the spoke is implemented at this point,
i. e. there are no subelements of ``/installation/hub/kdump``.

/installation/hub/keyboard
==========================
Handles :doc:`Keyboard <keyboard>` spoke.

/installation/hub/language_spoke
================================
Handles :doc:`Language Support <language>` spoke.

/installation/hub/luks_dialog
=============================
Equivalent to :ref:`recipe_elements/advanced_partitioning:/installation/hub/partitioning/advanced/luks_dialog`,
including child elements. 
It can be used in this place with kickstart installations using
``--encrypted`` without ``--passphrase``).

..
    /installation/hub/luks_dialog/cancel
    ====================================
    Equivalent to `/installation/hub/partitioning/advanced/luks_dialog/cancel`_

    /installation/hub/luks_dialog/confirm_password
    ==============================================
    Equivalent to `/installation/hub/partitioning/advanced/luks_dialog/confirm_password`_

    /installation/hub/luks_dialog/keyboard
    ======================================
    Equivalent to `/installation/hub/partitioning/advanced/luks_dialog/keyboard`_

    /installation/hub/luks_dialog/password
    ======================================
    Equivalent to `/installation/hub/partitioning/advanced/luks_dialog/password`_

    /installation/hub/luks_dialog/save
    ==================================
    Equivalent to `/installation/hub/partitioning/advanced/luks_dialog/save`_

/installation/hub/oscap_addon
=============================
Handles `Security Profile <oscap_addon>` spoke.

Attributes:

* ``fail_type`` - failure type shown on the spoke selector (button), depending
    on the reason (``not_ready``, ``misconfiguration_detected``, ``warnings_appeared`` or
    ``content_fetch_load_error``), used to distinguish the specific reason where necessary.
* ``expected_message`` - expected status message on the spoke selector (button)

/installation/hub/partitioning
==============================
Handles :doc:`Installation Destination <partitioning>` spoke.

/installation/hub/root
======================
Shortcut element usable only within ``ez:`` :ref:`namespace <recipe_elements/index:the *ez* namespace>`
to potentially make the recipe simpler by implicitly creating an `/installation/hub/root_password`_
element after :ref:`preprocessing <recipe_elements/index:the *ez* namespace>`.

It also creates necessary subelements to arrange for automatic filling in of password
and confirmation password based on ``password`` attribute value and successfully exiting
the spoke by clicking on Done button twice, using ``may_fail`` policy.

Attributes:

* ``password``

/installation/hub/root_password
===============================
Handles :doc:`Root Password <root_password>` spoke.

/installation/hub/software_selection
====================================
Handles :doc:`Software Selection <software_selection>` spoke.

Attributes:

* ``save-selection`` - save information about software selection (environment
    and addons) into ``/root/anabot-packageset.txt`` in the installed system -
    ``yes`` or ``no`` (default)

/installation/hub/syspurpose
============================
Handles :doc:`System Purpose <syspurpose>` spoke.

