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

/installation/welcome/os_name
=============================
Checks that the operating system name is shown on the welcome screen. The
``value`` is expected in two labels: the ``WELCOME TO ...`` label and the
``... INSTALLATION`` label. The product name is matched upper-cased (anaconda
upper-cases it in these labels) and the version is ignored. The check passes
only when the name is found in both labels.

Attributes:

* ``value`` - the operating system name expected on the welcome screen
    (e. g. ``Red Hat Enterprise Linux``)

/installation/welcome/storage_error_dialog
==========================================
Handles storage error dialogs that appears in case of storage state issue
(e. g. when two LVM volume groups with the same name are present).

Attributes:

* ``action`` - ``retry``, ``exit`` or ``noaction`` (doesn't touch the dialog)
* ``err_type`` - *beginning* of the particular error string
    (e. g. ``multiple LVM volume groups with the same name``)
