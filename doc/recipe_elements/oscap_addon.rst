======================
Security Profile spoke
======================

/installation/hub/oscap_addon/apply_policy
==========================================
Handles *Apply security policy:* toggle switch

Attributes:

* ``action`` - ``enable`` or ``disable``

/installation/hub/oscap_addon/change_content
============================================
Handles *Change content* button and resulting subspoke for content selection.

/installation/hub/oscap_addon/change_content/done
=================================================
Equivalent to `/installation/hub/oscap_addon/done`_

/installation/hub/oscap_addon/change_content/fetch
==================================================
Handles *Fetch* button and error bar on the bottom of the screen if an error
occurs during content fetching.

Attributes:

* ``fail_type`` - failure/error type related to content fetching:
    * ``invalid_url``
    * ``no_content_found``
    * ``extraction_failed``
    * ``invalid_content``
    * ``network_error``
    * ``unhandled_message`` - other, unspecified error

/installation/hub/oscap_addon/change_content/source
===================================================
Handles security content source (URL) field.

Attributes:

* ``url``

/installation/hub/oscap_addon/change_content/use_ssg
====================================================
Handles *Use SCAP Security Guide* button that makes the user return back to the
main Security Profile spoke.

/installation/hub/oscap_addon/changes
=====================================
Handles list of changes (*Changes that were done or need to be done:*)
imposed by a selected security profile (usable only for checks).

**Note:** The elements for error/information/warning messages in the list are functionally
equivalent, as it's technically not possible to distinguish the exact type at this point.

/installation/hub/oscap_addon/changes/error
===========================================
Handles a line (message) in the changes list. Not specific for an error message at this
point (see related `note </installation/hub/oscap_addon/changes_>`_ for
``/installation/hub/oscap_addon/changes`` element).

Attributes:

* ``text`` - message text in the raw form (unformatted string)
* ``params`` (where applicable) - a space-separated list of parameters used for formatting
  of the message string

/installation/hub/oscap_addon/changes/info
==========================================
Functionally equivalent to `/installation/hub/oscap_addon/changes/error`_
at this point (see related `note </installation/hub/oscap_addon/changes_>`_ for
``/installation/hub/oscap_addon/changes`` element).

/installation/hub/oscap_addon/changes/warning
=============================================
Functionally equivalent to `/installation/hub/oscap_addon/changes/error`_
at this point (see related `note </installation/hub/oscap_addon/changes_>`_ for
``/installation/hub/oscap_addon/changes`` element).

/installation/hub/oscap_addon/choose
====================================
Chooses (in the sense of just highlighting an entry, not *activating* it) a security
profile from the list.

Attributes:

* ``mode`` - profile selection mode
    * ``manual`` (default) - profile with a particular name will be selected
    * ``random`` - a random profile will be selected, potentially including
        the current one
    * ``random_strict`` - a random profile will be selected, excluding the
        currently selected one
* ``profile`` - profile name as shown in the list (the first, bold line)

/installation/hub/oscap_addon/done
==================================
*Done* button.

/installation/hub/oscap_addon/select
====================================
Handles *Select profile* button (i. e. activates the chosen profile).

/installation/hub/oscap_addon/select_checklist
==============================================
Handles *Checklist* combo box (if available).

Attributes:

* ``id``

/installation/hub/oscap_addon/select_datastream
===============================================
Handles *Data stream* combo box (if available).

Attributes:

* ``id``

/installation/hub/oscap_addon/use_ssg
=====================================
Functionally equivalent to `/installation/hub/oscap_addon/change_content/use_ssg`_.
Needs to be used from this path in special cases (e. g. kickstart installation
with incorrect content fingerprint specified).
