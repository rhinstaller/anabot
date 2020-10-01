# -*- coding: utf-8 -*-

"""
This module runs in own deamon thread. It watches periodically changes in
desired files and sends them using via teres.
"""

import os, time
import glob
import threading
import teres
from teres.bkr_handlers import QUIET_FILE

reporter = teres.Reporter.get_reporter()
watched_files = [
    '/tmp/anaconda.log',
    '/tmp/ifcfg.log',
    '/tmp/packaging.log',
    '/tmp/program.log',
    '/tmp/storage.log',
    '/tmp/syslog',
]
globfiles = [
    '/tmp/anaconda-tb-*',
]

def mainloop():
    time.sleep(5) # FIXME: should be enough time for beaker handler to show up
    changes = {k: None for k in watched_files}
    while True:
        # add globfiles to changes (watched_files)
        for globfile in globfiles:
            for path in glob.glob(globfile):
                if path not in changes:
                    changes[path] = None

        for path, last_changed in changes.items():
            if not os.path.exists(path):
                continue
            changed = os.stat(path).st_mtime
            if last_changed is not None and last_changed >= changed:
                continue
            # modify time is greater than last registered, send the file
            reporter.send_file(path, flags={QUIET_FILE:True})
            reporter.log_debug("Sending updated file: %s" % path)
            changes[path] = changed
        time.sleep(5)

watch_thread = threading.Thread(target=mainloop)
watch_thread.daemon = True
watch_thread.start()
