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

