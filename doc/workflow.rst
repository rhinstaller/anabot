Basic workflow (needs update)
=============================

Framework for anaconda GUI testing.

Running anaconda+anabot manually
--------------------------------

1. Create anabot recipe xml and make it available for download via http. If unsure, you can look to `examples`. The simplest one is: `examples/minimal.xml`.

2. Prepare updates.img with test.

  .. code-block:: bash

    $ ./make_updates.sh ~/public_html/dogtail.img

3. Start anaconda with prepared anabot.img. Append on kernel cmdline::

    updates=http://myhost.example.com/~myuser/anabot.img graphical console=tty0 console=ttyS0 anabot=http://myhost.example.com/~myuser/recipe.xml

 * Anabot is started automatically via systemd. You can observe output of
   anabot using journalctl:

   .. code-block:: bash

     $ journalctl -fu anabot-prepare
     $ journalctl -fu anabot

 * If something went wrong, you can still put manually anaconda to desired
   state via GUI and then start anabot manually:

  1. prepare again updates.img on your system:

    .. code-block:: bash

      $ ./make_updates.sh ~/public_html/anabot.img

  2. On serial console of system run:

    .. code-block:: bash

      $ ./get_update.sh

  3. Start anabot:

    .. code-block:: bash

      $ ./start-anabot.py

 * To pause execution of anabot installation use ``<debug_stop />`` tag in
   your recipe. To resume installation, touch /var/run/anabot/resume file.

Running anaconda+anabot in Beaker
---------------------------------

There are modules for anabot which allow it to run in beaker environment and
directly send results to beaker in real time. The module itself however
embeds also configuration and knowledge about infrastructure and cannot be
therefore documented here. Unfortunately, making it ready for open-sourcing
is at the bottom of todo list.

Interactive python shell
------------------------

To be able to use anabot in python shell to interact with anaconda directly,
just execute script `debug_dogtail.py` available in `/opt`.

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
