==============================
Installation Destination spoke
==============================

/installation/hub/partitioning/add_specialized_disk
===================================================
Handles *Add a disk...* in *Specialized & Network Disks* and related subspoke.

/installation/hub/partitioning/add_specialized_disk/done
========================================================
*Done* button.

/installation/hub/partitioning/add_specialized_disk/select
==========================================================
Handles (de)selection of available specialized disks.

Attributes:

* ``action`` - ``select`` or ``deselect`` (or anything else == deselect)
* ``invert_selection`` - inverts the selection logic (``0|off|false`` - default or ``1|on|true``)
* ``name`` - disk name or *glob*-like expression

/installation/hub/partitioning/additional_space
===============================================
*I would like to make additional space available.* check box.

Attributes:

* ``action`` - ``enable`` (default) or ``disable``

/installation/hub/partitioning/advanced
=======================================
Handles *Manual partitioning* subspoke.


/installation/hub/partitioning/disk
===================================
(De)selects disks from *Local Standard Disks* section of *Installation Destination*
spoke. Note that the logic of disks handling is based on knowledge of Anaconda's
behaviour of implicit disk selection in various scenarios (manual vs. interactive
kickstart installation), not the (graphical) disk selection status in the GUI.
The reason is that it's not possible to get the information about which disk icons
contain the selection mark via Dogtail/ATK at this point.

Attributes:

* ``name`` - disk name or glob pattern
* ``action`` - ``select`` or ``deselect``

/installation/hub/partitioning/done
===================================
*Done* button.

/installation/hub/partitioning/encrypt_data
===========================================
*Encrypt my data* check box at the bottom of *Installation Destination* spoke.

Attributes:

* ``action`` - ``enable`` or ``disable``

/installation/hub/partitioning/luks_dialog
===================================================
Handles *Disk Encryption Passphrase* dialog.

/installation/hub/partitioning/luks_dialog/cancel
==========================================================
Cancels the *Disk Encryption Passphrase* dialog.

/installation/hub/partitioning/luks_dialog/confirm_password
====================================================================
*Confirm:* password field in *Disk Encryption Passphrase* dialog.

Attributes:

* ``value``

/installation/hub/partitioning/luks_dialog/keyboard
============================================================
Switches keyboard layout to a required one in *Disk Encryption Passphrase* dialog.

Attributes:

* ``layout``

/installation/hub/partitioning/luks_dialog/password
============================================================
*Passphrase* field in *Disk Encryption Passphrase* dialog.

Attributes:

* ``value``

/installation/hub/partitioning/luks_dialog/save
========================================================
Confirms the *Disk Encryption Passphrase* dialog (clicks on *Save Passphrase* button).

/installation/hub/partitioning/mode
===================================
Handles *Storage Configuration* radio buttons to choose partitioning mode.

Attributes:

* ``mode`` - partitioning mode:
    * ``default`` - default, don't touch the preselected value
    * ``automatic`` - *Automatic*
    * ``manual`` - *Custom*
    * ``blivet`` - *Advanced Custom (Blivet GUI)*

/installation/hub/partitioning/reclaim
======================================
Handles *Reclaim Disk Space* dialog presented when Automatic partitioning
mode is confirmed.

Attributes:

* ``action`` - **Not implemented at this point** - ``reclaim`` or ``cancel``

/installation/hub/partitioning/reclaim/delete_all
=================================================
Handles *Delete all* button in *Reclaim Disk Space* dialog.
