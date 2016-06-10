Anabot
======
Framework for anaconda GUI testing.

Manual howto
-----

Prepare updates.img containing anabot:

    $ ./make_updates.sh ~/public_html/dogtail.img

Prepare anabot recipe (xml) and make it available on http/ftp. There are some
examples in git.

Manual test: start anaconda with prepared anabot.img. Append on kernel cmdline:

    updates=http://myhost.example.com/~myuser/anabot.img anabot=http://myhost.example.com/~myuser/recipe.xml graphical console=ttyS0

Anabot is started automatically via systemd. You can observe output of anabot using journalctl:

    $ journalctl -fu anabot-prepare
    $ journalctl -fu anabot

To pause execution of anabot installation use `<debug_stop />` tag in your recipe. To resume installation, touch /var/run/anabot/resume file.

Beaker job
----------
For beaker job, all you need to do, is use /anaconda/interactive/anabot7 task.
This task accepts following test params:
 * `UPDATES_URL` (optional)
 * `ANABOT_RECIPE_URL` (mandatory)
 * `INSTALL_BEAKERLIB` (optional)

`UPDATES_URL` lets you change URL to updates image with anabot to custom one
(e.g. for testing).

`ANABOT_RECIPE_URL` is mandatory and points to desired anabot recipe, e.g. https://gitlab.example.com/user/path/default.xml

`INSTALL_BEAKERLIB` specifies, if beakerlib should be installed after the
installation is complete. This may be required for other tests to run after
anabot task is complete. Beakerlib is installed, if the value is not equal 0.
Default is 0.
