=================
Time & Date spoke
=================

/installation/hub/datetime/city
===============================
*City* combo box.

Attributes:

* ``value``

/installation/hub/datetime/date
===============================
Date represented by the day/month/year combo boxes.

/installation/hub/datetime/date/day
===================================
*Day* combo box.

Attributes:

* ``value``

/installation/hub/datetime/date/month
=====================================
*Month* combo box.

Attributes:

* ``value``

/installation/hub/datetime/date/year
====================================
*Year* combo box.


Attributes:

* ``value``

/installation/hub/datetime/ntp
==============================
*Network time* toggle button.

Attributes:

* ``action`` - ``enable`` or ``disable``

/installation/hub/datetime/ntp_settings
=======================================
Handles NTP settings dialog, accessed by the 'gears' NTP settings button.

Attributes:

* ``dialog`` - ``accept`` (confirms the settings), ``dialog`` (cancels the dialog)

/installation/hub/datetime/ntp_settings/add
===========================================
Add an NTP server to the list.

Attributes:

* ``hostname`` - server hostname to add

/installation/hub/datetime/ntp_settings/disable
===============================================
Disable an NTP server from the list.

Attributes:

* ``hostname`` - server hostname to disable

/installation/hub/datetime/ntp_settings/enable
==============================================
Enable an NTP server from the list.

Attributes:

* ``hostname`` - server hostname to enable

/installation/hub/datetime/ntp_settings/rename
==============================================
Rename an existing server from the list.

Attributes:

* ``old`` - (old) server hostname to rename
* ``new`` - new server hostname

/installation/hub/datetime/region
=================================
*Region* combo box.

Attributes:

* ``value``

/installation/hub/datetime/time
===============================
Time-related configuration.

/installation/hub/datetime/time/ampm
====================================
Set AM/PM.

Attributes:

* ``value``

/installation/hub/datetime/time/format
======================================
Time format (24-hour or AM/PM) radio buttons.

Attributes:

* ``value`` - ``24`` for 24hour format or ``12`` for 12 (AM/PM) format

/installation/hub/datetime/time/hours
=====================================
Hours value.

Attributes:

* ``value``

/installation/hub/datetime/time/minutes
=======================================
Minutes value.

Attributes:

* ``value``
