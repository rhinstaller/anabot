Basic workflow
==============

Framework for anaconda GUI testing.

Disclaimer
----------
Currently, it is possible only to start GUI test manually.
The code is only in proof of concept stage right now.

Getting started
---------------

Prepare updates.img with test.

.. code-block:: bash

    $ ./make_updates.sh ~/public_html/dogtail.img

Start anaconda with prepared anabot.img. Append on kernel cmdline: ::

    updates=http://myhost.example.com/~myuser/anabot.img graphical console=tty0 console=ttyS0

Anabot is started automatically via systemd. You can observe output of anabot
using journalctl:

.. code-block:: bash

    $ journalctl -fu anabot-prepare
    $ journalctl -fu anabot

If something went wrong, you can still put manually anaconda to desired state
via GUI and then prepare again updates.img on your system:

.. code-block:: bash

    $ ./make_updates.sh ~/public_html/anabot.img

Then on serial console of system run:

.. code-block:: bash

    $ ./get_update.sh

And start anabot:

.. code-block:: bash

    $ ./start-anabot.py

If you want to specify your own anabot recipe, you can do it via kernel command
line, option named anabot. Eg: ::

    anabot=http://myhost.example.com/~myuser/recipe.xml

To pause execution of anabot installation use ``<debug_stop />`` tag in your
recipe. To resume installation, touch /var/run/anabot/resume file.

Interactive python shell
------------------------

To be able to use anabot in python shell to interact with anaconda directly
copy and paste following lines into the terminal on testing machine:

.. code-block:: bash

    export PYTHONPATH=/opt/lib/python2.7/site-packages
    export DISPLAY=:1
    cd /opt
    ./dump.py
    python
    import dogtail.utils
    dogtail.utils.enableA11y()
    from dogtail.predicate import GenericPredicate
    import dogtail.tree
    app_node = dogtail.tree.root.child(roleName="application", name="anaconda")
    from anabot.runtime.functions import waiton, waiton_all, getnode, getnodes, getparent, getparents, getsibling, hold_key, release_key
    from anabot.runtime.translate import set_languages, tr
    set_languages(['cs_CZ', 'cs'])

Anabot log
----------

If testing anabot in virtual machine there is a way to reach the anabot log from
the host machine.

1. Open the target virtual machine in virt-manager and select virtual hardware
   settings tab.

2. Click *Add Hardware* and select *Channel*.

3. Switch device type to *Output to a file (file)*.

4. Modify *Name* to *com.redhat.anabot.0*.

5. Select path where the log should be stored on the host system.
