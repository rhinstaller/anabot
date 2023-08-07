=============
Initial Setup
=============

/initial_setup
==============
Main element for *Initial Setup* testing.

/initial_setup/create_user
==========================
Handles *User Creation* spoke. It is functionally equivalent to
:doc:`/anaconda/hub/create_user <create_user>`.

/initial_setup/finish
=====================
Clicks on *Finish Configuration* button.

/initial_setup/license
======================
Handles *License Information* spoke.

/initial_setup/license/accept_license
=====================================
*I accept the license agreement* checkbox.

Attributes:

* checked - ``yes`` or ``no``

/initial_setup/license/done
===========================
*Done* button.

/initial_setup/license/eula
===========================
Useful only as a check (doesn't perform any action). It tests whether
the displayed license text is equivalent to ``/usr/share/redhat-release/EULA``.

/initial_setup/quit
===================
Clicks on *Quit* button.

/initial_setup/subscription_manager
===================================
Handles *Subscription Manager* spoke.

/initial_setup/subscription_manager/account_panel
=================================================
Configuration within subscription account panel.

/initial_setup/subscription_manager/account_panel/back
======================================================
*Back* button.

/initial_setup/subscription_manager/account_panel/login
=======================================================
*Login* input field.

Attributes:

* ``value``

/initial_setup/subscription_manager/account_panel/password
==========================================================
*Password* input field.

Attributes:

* ``value``

/initial_setup/subscription_manager/account_panel/register
==========================================================
*Register* button.

/initial_setup/subscription_manager/account_panel/system_name
=============================================================
*System Name* input field.

Attributes:

* ``value``

/initial_setup/subscription_manager/done
========================================
*Done* button.

/initial_setup/subscription_manager/server_panel
================================================
Configuration within subscription server panel.

/initial_setup/subscription_manager/server_panel/back
=====================================================
*Back* button.

/initial_setup/subscription_manager/server_panel/default_server
===============================================================
Clicks on *Default* button (in handler) to setup a default server
and checks (in check) whether the server field contains a default,
expected value (**this is likely outdated**).

/initial_setup/subscription_manager/server_panel/next
=====================================================
*Next* button.

/initial_setup/subscription_manager/server_panel/proxy
======================================================
*Configure Proxy* button and related *Proxy Configuration* dialog.

/initial_setup/subscription_manager/server_panel/proxy/cancel
=============================================================
Cancel the *Proxy Configuration* dialog.

/initial_setup/subscription_manager/server_panel/proxy/proxy_server
===================================================================
*Proxy Location* input field.

Attributes:

* ``value``

/initial_setup/subscription_manager/server_panel/proxy/save
===========================================================
*Save* button to accept proxy confguration dialog.

/initial_setup/subscription_manager/server_panel/proxy/test_connection
======================================================================
*Test Connection* button.

/initial_setup/subscription_manager/server_panel/proxy/use_proxy
================================================================
*I would like to connect via an HTTP proxy* checkbox.

Attributes:

* checked - ``yes`` or ``no``

/initial_setup/subscription_manager/server_panel/server
=======================================================
Subscription server (*I will register with*) input field.

Attributes:

* ``value``

/initial_setup/subscription_manager/sla_panel
=============================================
Configuration within service level agreement panel.

/initial_setup/subscription_manager/sla_panel/back
==================================================
*Back* button.

/initial_setup/subscription_manager/sla_panel/next
==================================================
*Next* button.

/initial_setup/subscription_manager/sla_panel/sla
=================================================
Service level agreement combo box.

Attributes:

* ``value``

/initial_setup/subscription_manager/subscription_panel
======================================================
Configuration within subscription panel.

/initial_setup/subscription_manager/subscription_panel/attach
=============================================================
*Attach* button.

/initial_setup/subscription_manager/subscription_panel/back
===========================================================
*Back* button.

/initial_setup/subscription_manager/subscription_panel/subscriptions
====================================================================
No action, only checks that subscriptions table contains
some subscription.

