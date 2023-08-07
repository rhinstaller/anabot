==============
Welcome screen
==============

/installation/welcome/beta_dialog
=================================
Handles Beta dialog.

Attributes:

* ``dialog`` - ``accept`` or ``reject``

/installation/welcome/continue
==============================
*Continue* button on the welcome screen.

/installation/welcome/language
==============================
Handles choice of language on the welcome screen.

Attributes:

* ``value``

/installation/welcome/locality
==============================
Handles choice of language locality on the welcome screen.

Attributes:

* ``value``

/installation/welcome/storage_error_dialog
==========================================
Handles storage error dialogs that appears in case of storage state issue
(e. g. when two LVM volume groups with the same name are present).

Attributes:

* ``action`` - ``retry``, ``exit`` or ``noaction`` (doesn't touch the dialog)
* ``err_type`` - *beginning* of the particular error string
    (e. g. ``multiple LVM volume groups with the same name``)
