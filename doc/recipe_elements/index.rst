###############
Recipe elements
###############

********
Overview
********

The Anabot recipe is an XML file consisting of specific elements.
Here's an overview of supported elements, represented as a path in the
tree-like structure of the file for a better readability.

There are two main areas (applications) covered by Anabot - Anaconda and Initial Setup.

As Anabot uses *handlers* (functions typically performing an actual action in the GUI)
and *checks* (functions checking that the action took place in an expected way); they
return results based on whether the action/check was successful.

The expected outcome can be defined by ``policy`` attribute of any element in the recipe
(when description of any element below states that it takes no attributes, it means arguments
*specific* for the particular element) and it can contain the following values:

* ``should_pass`` (implicit value) - the element's handler should be executed and
    it is expected that check result should be successful
* ``should_fail`` - similar, but the check is expected to fail
* ``just_check`` - don't execute the handler (don't perform any action), only check
    the expected resulting state (e. g. an input field contains expected text)
* ``just_check_fail`` - don't perform any action, only check that the expected result
    is **not** present

A small subset of elements (e. g. :doc:`/installation/hub/oscap_addon <oscap_addon>`)
also supports ``fail_type`` attribute, which can be used for a finer handling of the
specific failure reason.

.. note::

    The elements description below describe available attributes and their meanings and values.
    If a meaning and/or allowed values of an attribute aren't mentioned explicitly, they are
    considered obvious from the context (i. e. ``value`` attribute for a text input field).

    In a similar way, some attributes take binary values by nature (e. g. enable/disable,
    accept/reject), but technically, on implementation level, one of the values is
    exactly specified (e. g. ``enable``) and the complementary one can be
    represented by any, unspecified value (e. g. ``disable``, ``disabled`` or even ``foobar``).
    In such cases the following descriptions can specify a specific value even on places
    where an arbitrary (complementary, unspecified) one could be used for the sake of
    clarity. It is strongly advised to only use those specified values so as to
    make things easy to understand and consistent, instead of some arbitrary ones,
    despite their functional equivalence.

********
Anaconda
********

The *ez* namespace
==================
Anabot's preprocessor supports omitting parts of the recipe (elements or attributes)
while creating the necessary attributes itself, thus making the recipe creation
somewhat easier and more readable.

This can be achieved by using the ``ez`` prefix within the supported elements
(after first defining the namespace).

For instance, a recipe containing just

.. code-block:: xml

    <ez:installation xmlns:ez="http://fedoraproject.org/anaconda/anabot/recipe/tiny/1">
        <ez:hub>
            <kdump />
        </ez:hub>
    </ez:installation>

will expand into a functionally complete minimal recipe containing the explicitly defined
parts (``<kdump />``), with the rest generated automatically by preprocessor:

.. code-block:: xml

    <?xml version="1.0"?>
    <installation>
      <welcome _default_for="/ez:installation">
        <continue _default_for="/ez:installation"/>
        <beta_dialog policy="should_fail" _default_for="/ez:installation"/>
      </welcome>
      <hub>
        <kdump/>
        <partitioning _default_for="/ez:installation/ez:hub">
          <add_specialized_disk _default_for="/ez:installation/ez:hub">
            <select name="*" _default_for="/ez:installation/ez:hub"/>
            <done _default_for="/ez:installation/ez:hub"/>
          </add_specialized_disk>
          <disk name="*" action="select" _default_for="/ez:installation/ez:hub"/>
          <mode mode="automatic" _default_for="/ez:installation/ez:hub"/>
          <additional_space action="enable" _default_for="/ez:installation/ez:hub"/>
          <done _default_for="/ez:installation/ez:hub"/>
          <reclaim _default_for="/ez:installation/ez:hub">
            <delete_all _default_for="/ez:installation/ez:hub"/>
          </reclaim>
        </partitioning>
        <root_password _default_for="/ez:installation/ez:hub">
          <password value="fo0m4nchU1" _default_for="/ez:installation/ez:hub"/>
          <confirm_password value="fo0m4nchU1" _default_for="/ez:installation/ez:hub"/>
          <done _default_for="/ez:installation/ez:hub"/>
        </root_password>
        <begin_installation _default_for="/ez:installation/ez:hub"/>
      </hub>
      <configuration _default_for="/ez:installation">
        <wait_until_complete _default_for="/ez:installation"/>
        <reboot _default_for="/ez:installation"/>
      </configuration>
    </installation>

The following elements can be used with the ``ez`` namespace (see specific sections for
descriptions of particular elements):

* `/installation`_
* `/installation/welcome`_
* :ref:`recipe_elements/hub:/installation/hub`
* :ref:`recipe_elements/hub:/installation/hub/autopart`
* :ref:`recipe_elements/hub:/installation/hub/root_password`
* :ref:`recipe_elements/hub:/installation/hub/root`
* :ref:`recipe_elements/configuration:/installation/configuration/root_password`
* :ref:`recipe_elements/configuration:/installation/configuration/root`

/installation
=============
This is the *main* element for Anaconda testing. It doesn't have any attributes.

/installation/welcome
=====================
Handles welcome screen (*Welcome to Red Hat Enterprise Linux X.Y*).

*************
Initial Setup
*************
Described in :doc:`initial_setup`.

****************
Special elements
****************
There are two special elements that can be used in any place of the recipe:

debug_stop
==========
When this element is handled, processing of the recipe stops. This can be, for instance, useful
when designing a new recipe or handling issues with an existing one, without a need to process
the whole recipe.
Similarly it can be used when implementing new functionality in Anabot for debugging purposes.

Processing of the recipe continues when Anabot detects existing ``/var/run/anabot/resume`` file
(i. e. when you run ``touch /var/run/anabot/resume``).

script
======
Arbitrary script snippet.

Attributes:

* ``interpret`` - interpreter used for script execution (``/bin/bash`` by default)
* ``log_name`` - log name (for script output) relative to ``/var/run/anabot``
    in installer environment

***************************
Detailed elements reference
***************************
.. toctree::
    :caption: Anaconda
    :maxdepth: 2

    welcome
    hub
    keyboard
    language
    datetime
    connect_to_redhat
    create_user
    root_password
    installation_source
    software_selection
    partitioning
    advanced_partitioning
    oscap_addon
    syspurpose
    configuration

.. toctree::
    :caption: Initial Setup
    :maxdepth: 2

    initial_setup