========================
Connect to Red Hat spoke
========================

/installation/hub/connect_to_redhat/account_organization
========================================================
Combo box that appears for user in multiple organizations.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/activation_key
==================================================
Input field - *Activation Key*.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/authentication
==================================================
*Authentication* radio button.

Attributes:

* ``type`` - ``account`` or ``activation key``

/installation/hub/connect_to_redhat/insights
============================================
*Connect to Red Hat Insights* check box.

Attributes:

* ``checked`` - ``yes`` or ``no``

/installation/hub/connect_to_redhat/options
===========================================
Connection *Options* (HTTP proxy, custom server URL and base URL).

/installation/hub/connect_to_redhat/options/custom_base_url
===========================================================
*Custom base URL* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/options/custom_server_url
=============================================================
*Custom server URL* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/options/http_proxy
======================================================
*Use HTTP proxy* checkbox (and related proxy settings handled
in child elements - see below).

Attributes:

* ``used`` - ``yes`` = enabled, anything else = disabled

/installation/hub/connect_to_redhat/options/http_proxy/location
===============================================================
HTTP proxy *Location* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/options/http_proxy/password
===============================================================
HTTP proxy *Password* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/options/http_proxy/username
===============================================================
HTTP proxy *User name* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/options/satellite_url
=========================================================
*Satellite URL* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/options/use_custom_base_url
===============================================================
*Custom base URL* check box.

Attributes:

* ``checked`` - ``yes`` or ``no``

/installation/hub/connect_to_redhat/options/use_custom_server_url
=================================================================
*Custom server URL* check box.

Attributes:

* ``checked`` - ``yes`` or ``no``

/installation/hub/connect_to_redhat/options/use_satellite_url
=============================================================
*Satellite URL* check box.

Attributes:

* ``checked`` - ``yes`` or ``no``

/installation/hub/connect_to_redhat/organization
================================================
*Organization* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/password
============================================
*Organization* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/register
============================================
*Register* button.

/installation/hub/connect_to_redhat/registration
================================================
Information about registration in registered state.

/installation/hub/connect_to_redhat/registration/account_organization
=====================================================================
Registered account organization.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/insights
=========================================================
Insights status in registered state. 

Attributes:

* ``used`` - ``yes`` or ``no``

/installation/hub/connect_to_redhat/registration/method
=======================================================
Registration method in registered state.

Attributes:

* ``account``
* ``organization``

/installation/hub/connect_to_redhat/registration/subscriptions
==============================================================
Attached subscriptions in registered state.

Attributes:

* ``amount`` - amount of expected subscriptions; ``-1`` means that the amount
  won't be checked, just the related label for 0/1/n subscriptions
* ``minAmount`` - minimal expected amount of subscriptions
* ``maxAmount`` - maximal expected amount of subscriptions

/installation/hub/connect_to_redhat/registration/subscriptions/subscription
===========================================================================
Name of subscription present in registered state.

Attributes:

* ``name`` - name or *fnmatchcase* expression for expected subscription

/installation/hub/connect_to_redhat/registration/subscriptions/subscription/contract
====================================================================================
Subscription contract in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/subscriptions/subscription/end_date
====================================================================================
Subscription end date in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/subscriptions/subscription/entitlements_consumed
=================================================================================================
Consumed entitlements in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/subscriptions/subscription/service_level
=========================================================================================
Subscription service level in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/subscriptions/subscription/sku
===============================================================================
Subscription SKU in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/subscriptions/subscription/start_date
======================================================================================
Subscription start date in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/system_purpose
===============================================================
System purpose in registered state, has no attributes.

/installation/hub/connect_to_redhat/registration/system_purpose/role
====================================================================
System purpose role in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/system_purpose/sla
===================================================================
System purpose SLA in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/registration/system_purpose/usage
=====================================================================
System purpose usage in registered state.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/system_purpose
==================================================
*Set System Purpose* check box.

Attributes:

* ``set`` - ``yes`` or ``no``

/installation/hub/connect_to_redhat/system_purpose/role
=======================================================
System purpose *Role* combo box.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/system_purpose/sla
======================================================
System purpose *SLA* combo box.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/system_purpose/usage
========================================================
System purpose *Usage* combo box.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/unregister
==============================================
*Unregister* button.

/installation/hub/connect_to_redhat/username
============================================
*User name* input field.

Attributes:

* ``value``

/installation/hub/connect_to_redhat/wait_until_registered
=========================================================
Element with a special meaning, blocking processing of further elements
until the registration process has completed, to ensure it took place
completely (successfully or unsuccessfully).
