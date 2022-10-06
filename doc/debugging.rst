=========
Debugging
=========

Debugging Tools
===============

**Log**
   Contains a lot of useful information ;)
   ``journalctl -u anabot``

**Dogtail dump**
   Dumps basic information about GUI elements currently displayed in anaconda into a text file ``/tmp/dogtail.dump``. Run ``/opt/dump.py`` then check ``/tmp/dogtail.dump``. Expect issues with encoding if language with special characters is selected in anaconda.

**Dogtail debug**
   This script ``/opt/debug_dogtail.py`` prepares everything you need for easy anabot code testing and debugging. For example by adding this short code you can print names of all buttons::

    for node in getnodes(app_node, "push button", sensitive=None):
        print(node.name)

**Tag debug stop**
   An anabot XML element that stops anabot execution and creates dogtail dump. To use it simply add ``<debug_stop />`` to anabot recipe and it will stop when it gets there. If you decide to resume the execution use ``touch /var/run/anabot/resume``

Tracebacks
==========
When traceback occurs in anabot there's a chance it will be able to upload the traceback dump to beaker. This can make it much easier to figure out what is wrong.

To read it download the file traceback.dump and run following commands from anabot git directory::

  PYTHONPATH=lib/python3.9/site-packages/:lib/x86_64/python3.9/ python3
  import pickle
  dump = pickle.load(open('traceback.dump', 'rb'))
  print("".join(d['stack'] for d in dump))

Examples
========

**Name of a GUI element changed**
   Symptoms: Anabot execution stopped.

   1. Check anabot log, don't get distracted by the end of the log, instead find the first FAIL::

       Jun 01 06:42:42 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-064242_debug ...
       Jun 01 06:42:42 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: :: [   FAIL   ] :: Check failed for: /installation/hub/root_password line: 17
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Reason was: Root password spoke selector not found or not clickable.
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-064243_debug ...
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: Removing duplicit screenshot
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Processing: /installation/hub/begin_installation
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-064243_debug.0 ...
       Jun 01 06:42:43 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       ...
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-064329_debug ...
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: begin_installation returns action_result
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: :: [   FAIL   ] :: Check failed for: /installation/hub/begin_installation line: 22
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Reason was: Couln't find clickable "Begin installation" button.
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-064329_debug.0 ...
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: Removing duplicit screenshot
       Jun 01 06:43:29 localhost python_launcher.sh[2265]: :: [   PASS   ] :: Check passed for: /installation/hub line: 7
       Jun 01 06:43:30 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-064329_debug.1 ...
       Jun 01 06:43:30 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:43:30 localhost python_launcher.sh[2265]: Removing duplicit screenshot
       Jun 01 06:43:30 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Processing: /installation/configuration
       Jun 01 06:43:30 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Waiting for yum transaction. Timeout is 10 minutes
       Jun 01 06:53:31 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-065330_debug ...
       Jun 01 06:53:31 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:53:31 localhost python_launcher.sh[2265]: Removing duplicit screenshot
       ...
       Jun 01 06:56:15 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-065615_debug ...
       Jun 01 06:56:15 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   FAIL   ] :: Check failed for: /installation/configuration line: 24
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Reason was: Couldn't find "CONFIGURATION" panel
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   INFO   ] :: Failure type was: panel_not_found
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-065616_debug ...
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Removing duplicit screenshot
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   ERROR  ] :: Check didn't return any result for: /installation line: 2
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   FAIL   ] :: Check failed for: /installation line: 2
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Creating logfile at /tmp/dogtail-root/logs/make_screenshot_20200601-065616_debug.0 ...
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Screenshot taken: /var/run/anabot/13-screenshot.png
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Removing duplicit screenshot
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   ERROR  ] :: Hook raised exception: [Errno 2] No such file or directory: '/mnt/sysimage/tmp/30-post.hook'
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   ERROR  ] :: Hook raised exception: [Errno 2] No such file or directory: '/mnt/sysimage/tmp/90-post.hook'
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   ERROR  ] :: Hook raised exception: [Errno 2] No such file or directory: '/mnt/sysimage/tmp/95-add_luks_key-post.hook'
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: :: [   ERROR  ] :: Hook raised exception: [Errno 2] No such file or directory: '/mnt/sysimage/tmp/98-post.hook'
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Running hook: /opt/modules/copy_logs/99-post-nochroot.hook
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: cp: cannot create regular file '/mnt/sysimage/root/anabot.log': No such file or directory
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: /opt/modules/copy_logs/99-post-nochroot.hook: line 6: /mnt/sysimage/root/anabot.journal.log: No such file or directory
       Jun 01 06:56:16 localhost python_launcher.sh[2265]: Hook exited with conde: 1
       Jun 01 06:56:17 localhost systemd[1]: anabot.service: Main process exited, code=exited, status=1/FAILURE
       Jun 01 06:56:17 localhost systemd[1]: anabot.service: Failed with result 'exit-code'.

   2. Looks like anabot can't find root password spoke, run ``/opt/dump.py`` and check the dump::

       [anaconda root@localhost ~]# /usr/libexec/platform-python /opt/dump.py 
       [anaconda root@localhost ~]# cat /tmp/dogtail.dump 
       [desktop frame | main]
        [application | metacity]
         [window | ]
        [application | anaconda]
         [frame | Anaconda Installer]
          [panel | ]
           [panel | ]
            [panel | PŘEHLED INSTALACE]
             [filler | ]
              [panel | ]
               [panel | ]
                [push button | Nápověda!]
                 [action | click |  ]
                [panel | Keyboard Layout]
                 [filler | ]
                  [icon | ]
                  [label | cz]
                [label | PŘEDPRODUKČNÍ / TESTOVACÍ]
                [label | INSTALACE RED HAT ENTERPRISE LINUX 8.3]
                [label | PŘEHLED INSTALACE]
              [panel | ]
               [filler | ]
                [scroll pane | ]
                 [viewport | ]
                  [panel | ]
                   [spoke selector | Vytvoření uživatele]
                    [panel | ]
                     [icon | ]
                     [label | Nebude vytvořen žádný uživatel]
                     [label | Vytvoření uživatele]
                   [spoke selector | Heslo správce]
                    [panel | ]
                     [icon | ]
                     [label | Účet uživatele root je vypnutý.]
                     [label | Heslo správce]
                   [label | NASTAVENÍ UŽIVATELŮ]
                   [spoke selector | Síť a název počítače]
                    [panel | ]
                     [icon | ]
                     [label | Drátové (enp1s0) připojeno]
                     [label | Síť a název počítače]
       ...

   3. We can see that the spoke has name "Heslo správce", now we need to find the translation. First we have to uncompile message catalog from binary format, then grep the string we are looking for::

       [anaconda root@localhost ~]# msgunfmt /usr/share/locale/cs/LC_MESSAGES/anaconda.mo > anaconda.po
       [anaconda root@localhost ~]# grep -B 2 'Heslo spr' anaconda.po 
       msgctxt "GUI|Password"
       msgid "_Root Password:"
       msgstr "_Heslo správce:"
       --
       msgctxt "GUI|Spoke"
       msgid "_Root Password"
       msgstr "_Heslo správce"
       --
       
       msgid "Root password"
       msgstr "Heslo správce systému"
       
       msgid "Root password is not set"
       msgstr "Heslo správce není nastaveno"
       
       msgid "Root password is set"
       msgstr "Heslo správce je nastaveno"

   4. Now open the corresponding source file located in ``anabot/runtime/``, in this case we have to modify ``anabot/runtime/installation/configuration/root_password.py`` and add missing underscore::

       SPOKE_SELECTOR="Root Password" > SPOKE_SELECTOR="_Root Password"

.. note:: Underscore marks the shortcut letter and must be included in the string although it usually isn't in the name

.. warning:: There may be more translations of the same string in different contexts, and are not always used correctly so watch out for that.
