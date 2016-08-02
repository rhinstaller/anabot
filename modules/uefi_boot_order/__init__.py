# -*- coding: utf-8 -*-

"""
This module copies UEFI boot order at the beginning of installation and tries
to re-order boot entries at the end of the installation so that netboot which
was previously present as first boot entry is again first boot entry.
"""

import subprocess

import teres
reporter = teres.Reporter.get_reporter()

from anabot.exceptions import UnrelatedException
from anabot.runtime.hooks import register_post_hook

def efiboot_entry(intext, key):
    lines = intext.split('\n')
    for line in lines:
        items = line.split()
        if items[0] == key:
            return items[1]

def boot_order(intext):
    return efiboot_entry(intext, 'BootOrder:').split(',')

def boot_current(intext):
    return efiboot_entry(intext, 'BootCurrent:')

if "ks=" in open('/proc/cmdline').read():
    raise UnrelatedException('Running in kickstart, UEFI boot order should be fixed by post script.')

try:
    efibootmgr_output = subprocess.check_output(['efibootmgr'])
except (subprocess.CalledProcessError, OSError):
    raise UnrelatedException('Efibootmgr call failed. The system is probably not running in UEFI mode.')

reporter.log_info("Going to fix UEFI boot order after installation.")
old_boot_order = boot_order(efibootmgr_output)
reporter.log_info("Original boot order is: %s" % ",".join(old_boot_order))
if old_boot_order is None:
    raise Exception("Couldn't find BootOrder in efibootmgr output.")

@register_post_hook(90)
def fix_boot_order():
    reporter.log_info("Fixing UEFI boot order.")
    changed_efibootmgr_output = subprocess.check_output(['efibootmgr'])
    changed_boot_order = boot_order(changed_efibootmgr_output)
    if set(changed_boot_order) == set(old_boot_order):
        new_boot_order = old_boot_order
        reporter.log_debug("New anaconda's bootorder contains same boot entry numbers. Using old bootorder.")
        reporter.log_debug("Old: %s" % ",".join(old_boot_order))
    else:
        reporter.log_debug("New anaconda's bootorder contains other set of boot entry number that the old one.")
        reporter.log_debug("Finding set of old entry numbers hoping to replace them by just one new entry number.")
        in_old = set(old_boot_order) - set(changed_boot_order)
        in_new = list(set(changed_boot_order) - set(old_boot_order))
        if len(in_new) != 1:
            reporter.log_error("New anaconda's bootorder contains more new entries that were in the original one.")
            reporter.log_error("Old: %s" % ",".join(old_boot_order))
            reporter.log_error("New: %s" % ",".join(changed_boot_order))
        in_new = in_new[0]
        def old_to_new(entry):
            if entry in in_old:
                return in_new
            return entry
        new_boot_order = [old_to_new(x) for x in old_boot_order]
    new_boot_order = ",".join(new_boot_order)
    reporter.log_info("Setting boot order to: %s" % new_boot_order)
    subprocess.check_call(['efibootmgr', '-o', new_boot_order])
    current = boot_current(efibootmgr_output)
    reporter.log_info("Setting next boot to: %s" % current)
    subprocess.check_call(['efibootmgr', '-n', current])
