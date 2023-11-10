============================
Manual Partitioning subspoke
============================


/installation/hub/partitioning/advanced/add
===========================================
Handles *add* (*+*) button and resulting dialog to add a new partition/LV.

Attributes:

* ``dialog`` - ``accept`` or ``reject``

/installation/hub/partitioning/advanced/add/mountpoint
======================================================
*Mount Point* input field for a newly added partition or LV.

Attributes:

* ``value``
* ``checked`` - ``yes`` or ``no``

/installation/hub/partitioning/advanced/add/size
================================================
Mount point for a newly added partition or LV in *Add a New Mount Point* dialog.


Attributes:

* ``value``

/installation/hub/partitioning/advanced/autopart
================================================
Desired capacity for a newly added partition or LV in *Add a New Mount Point* dialog.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details
===============================================
Handles device details for a selected partition/LV (the right part of the spoke).

/installation/hub/partitioning/advanced/details/device_type
===========================================================
*Device Type* combo box.

Attributes:

* ``select`` - device type according to following schema:
    * ``native`` - standard partition
    * ``btrfs``
    * ``lvm``
    * ``raid``
    * ``lvm thinp``

/installation/hub/partitioning/advanced/details/devices
=======================================================
Handles devices selection for a selected partition/LV (*Device(s):*/*Modify...*) button
and resulting dialog.

Attributes:

* ``dialog`` - ``accept`` or ``reject``

/installation/hub/partitioning/advanced/details/devices/deselect
================================================================
Deselects a device in *Configure Mount Point* dialog.

Attributes:

* ``device`` - device name or glob pattern

/installation/hub/partitioning/advanced/details/devices/select
==============================================================
Selects a device in *Configure Mount Point* dialog.

Attributes:

* ``device`` - device name or glob pattern

/installation/hub/partitioning/advanced/details/edit_volume_group
=================================================================
Handles *Modify...* button for Volume Group related to selected LV and
resulting *Configure Volume Group* dialog.

Attributes:

* ``dialog`` - ``accept`` or ``reject``

/installation/hub/partitioning/advanced/details/edit_volume_group/devices
=========================================================================
Handles selection of devices related to a particular VG in
*Configure Volume Group* dialog. **Currently not implemented.**

/installation/hub/partitioning/advanced/details/edit_volume_group/encrypt
=========================================================================
*Encrypt* check box in *Configure Volume Group* dialog.

Attributes:

* ``value`` - ``yes`` or ``no``

/installation/hub/partitioning/advanced/details/edit_volume_group/luks_version
==============================================================================
*LUKS Version* combo box in in *Configure Volume Group* dialog.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/edit_volume_group/name
======================================================================
VG *name* in *Configure Volume Group* dialog.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/edit_volume_group/raid
======================================================================
*RAID Level* combo box in *Configure Volume Group* dialog.

Attributes:

* ``select`` - level of RAID

/installation/hub/partitioning/advanced/details/edit_volume_group/size
======================================================================
Size field value in *Configure Volume Group* dialog.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/edit_volume_group/size_policy
=============================================================================
*Size policy* combo box in *Configure Volume Group* dialog.

Attributes:

* ``select`` - size policy type (``fixed``, ``maximum`` or ``auto``)

/installation/hub/partitioning/advanced/details/encrypt
=======================================================
*Encrypt* check box in partition/LV details.

Attributes:

* ``action`` - ``enable`` or ``disable``

/installation/hub/partitioning/advanced/details/filesystem
==========================================================
*File System* combo box in partition/LV details.

Attributes:

* ``select`` - FS type

/installation/hub/partitioning/advanced/details/label
=====================================================
*Label* input field in partition/LV details.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/luks_unlock
===========================================================
Handles unlocking of a selected LUKS device by (optionally) entering
a provided password in the passphrase field and clicking on Unlock button.

Attributes:

* ``password`` (optional) - LUKS password. If password is not specified,
  Anabot will only click on the Unlock button, without entering any
  password. This may be useful if the password was already entered before
  (e. g. after a disk rescan).

/installation/hub/partitioning/advanced/details/mountpoint
==========================================================
*Mount Point* input field in partition/LV details.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/name
====================================================
*Name* input field in partition/LV details.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/new_volume_group
================================================================
Creates a new volume group using *Volume Group* combo box &rarr;
*Create a new volume group...*

Attributes:

* ``value``
* ``checked`` - ``yes`` or ``no``

/installation/hub/partitioning/advanced/details/new_volume_group/devices
========================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/devices`_

/installation/hub/partitioning/advanced/details/new_volume_group/encrypt
========================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/encrypt`_

/installation/hub/partitioning/advanced/details/new_volume_group/luks_version
=============================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/luks_version`_

/installation/hub/partitioning/advanced/details/new_volume_group/name
=====================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/name`_

/installation/hub/partitioning/advanced/details/new_volume_group/raid
=====================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/raid`_

/installation/hub/partitioning/advanced/details/new_volume_group/size
=====================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/size`_

/installation/hub/partitioning/advanced/details/new_volume_group/size_policy
============================================================================
Functionally equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/size_policy`_

/installation/hub/partitioning/advanced/details/raid_type
=========================================================
*RAID Level* combo box in partition/LV details.

Attributes:

* ``select``

/installation/hub/partitioning/advanced/details/reformat
========================================================
*Reformat* check box in partition/LV details.

Attributes:

* ``action`` - ``check`` or ``uncheck``

/installation/hub/partitioning/advanced/details/size
====================================================
*Desired Capacity* input field in partition/LV details.

Attributes:

* ``value``

/installation/hub/partitioning/advanced/details/update
======================================================
Clicks on *Update Settings* button in partition/LV details.

/installation/hub/partitioning/advanced/done
============================================
*Done* button

/installation/hub/partitioning/advanced/encrypt_data
====================================================
*Encrypt my data* check box on the left side of *Manual Partitioning* subspoke
present before automated creation of partitioning layout.

Attributes:

* ``action`` - ``enable`` or ``disable``

/installation/hub/partitioning/advanced/luks_dialog
===================================================
Equivalent to :ref:`recipe_elements/partitioning:/installation/hub/partitioning/luks_dialog`
(including child elements).

..
    /installation/hub/partitioning/advanced/luks_dialog/cancel
    ==========================================================
    Cancels the *Disk Encryption Passphrase* dialog.

    /installation/hub/partitioning/advanced/luks_dialog/confirm_password
    ====================================================================
    *Confirm:* password field in *Disk Encryption Passphrase* dialog.

    Attributes:

    * ``value``

    /installation/hub/partitioning/advanced/luks_dialog/keyboard
    ============================================================
    Switches keyboard layout to a required one in *Disk Encryption Passphrase* dialog.

    Attributes:

    * ``layout``

    /installation/hub/partitioning/advanced/luks_dialog/password
    ============================================================
    *Passphrase* field in *Disk Encryption Passphrase* dialog.

    Attributes:

    * ``value``

    /installation/hub/partitioning/advanced/luks_dialog/save
    ========================================================
    Confirms the *Disk Encryption Passphrase* dialog (clicks on *Save Passphrase* button).

/installation/hub/partitioning/advanced/remove
==============================================
Handles *remove* (*-*) button and the resulting confirmation dialog.

Attributes:

* ``dialog`` - ``accept`` or ``reject``

/installation/hub/partitioning/advanced/remove/also_related
===========================================================
Handles *Delete all file systems which are only used by Red Hat Enterprise Linux X.Y
for <arch>* check box.

Attributes:

* ``value`` - ``yes`` or ``no``

/installation/hub/partitioning/advanced/rescan
==============================================
Handles *Reload storage configuration from disk* (rescan) button and related dialog.

Attributes:

* ``dialog`` - ``accept`` or ``reject``

/installation/hub/partitioning/advanced/rescan/push_rescan
==========================================================
Clicks on *Rescan Disks* button in *Rescan Disks* dialog.

/installation/hub/partitioning/advanced/schema
==============================================
Handles partitioning schema (*New mount points will use the following 
partitioning scheme:*) combo box.

Attributes:

* ``value`` - device type according to following schema:
    * ``native`` - standard partition
    * ``btrfs``
    * ``lvm``
    * ``raid``
    * ``lvm thinp``

/installation/hub/partitioning/advanced/select
==============================================
Shortcut to select and handle a set of available partitions/LVs based
on specified criteria.

Attributes:

* ``device`` - device name (e. g. `/dev/vda`) or glob pattern
* ``mountpoint`` - mount point path (or glob pattern)

/installation/hub/partitioning/advanced/select/details
======================================================
Configures details for selected partition(s)/LV(s) in the same way as
`/installation/hub/partitioning/advanced/details`_, including child elements.

..
    It's likely not necessary to repeat the already mentioned paths/elements:

    /installation/hub/partitioning/advanced/select/details/device_type
    ==================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/device_type`_.

    /installation/hub/partitioning/advanced/select/details/devices
    ==============================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/devices`_.

    /installation/hub/partitioning/advanced/select/details/devices/deselect
    =======================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/devices/deselect`_.

    /installation/hub/partitioning/advanced/select/details/devices/select
    =====================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/devices/select`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group
    ========================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/devices
    ================================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/devices`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/encrypt
    ================================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/encrypt`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/luks_version
    =====================================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/luks_version`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/name
    =============================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/name`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/raid
    =============================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/raid`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/size
    =============================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/size`_.

    /installation/hub/partitioning/advanced/select/details/edit_volume_group/size_policy
    ====================================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/edit_volume_group/size_policy`_.

    /installation/hub/partitioning/advanced/select/details/encrypt
    ==============================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/encrypt`_.

    /installation/hub/partitioning/advanced/select/details/filesystem
    =================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/filesystem`_.

    /installation/hub/partitioning/advanced/select/details/label
    ============================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/label`_.

    /installation/hub/partitioning/advanced/select/details/mountpoint
    =================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/mountpoint`_.

    /installation/hub/partitioning/advanced/select/details/name
    ===========================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/name`_.

    /installation/hub/partitioning/advanced/select/details/new_volume_group
    =======================================================================
    Equivalent to `/installation/hub/partitioning/advanced/details/new_volume_group`_.

    /installation/hub/partitioning/advanced/select/details/new_volume_group/devices
    ===============================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/new_volume_group/encrypt
    ===============================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/new_volume_group/luks_version
    ====================================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/new_volume_group/name
    ============================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/new_volume_group/raid
    ============================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/new_volume_group/size
    ============================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/new_volume_group/size_policy
    ===================================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/raid_type
    ================================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/reformat
    ===============================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/size
    ===========================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

    /installation/hub/partitioning/advanced/select/details/update
    =============================================================


    Attributes:

    * ``value``
    * ``checked`` - ``yes`` or ``no``

/installation/hub/partitioning/advanced/select/remove
=====================================================
Equivalent to `/installation/hub/partitioning/advanced/remove`_.


/installation/hub/partitioning/advanced/select/remove/also_related
==================================================================
Equivalent to `/installation/hub/partitioning/advanced/remove/also_related`_.

/installation/hub/partitioning/advanced/summary
===============================================
Handles *Summary of Changes* dialog.

Attributes:

* ``dialog`` - ``accept`` or ``reject``
