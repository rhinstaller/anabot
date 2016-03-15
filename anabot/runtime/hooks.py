# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

import os, shutil, subprocess, stat

def _hooks(event):
    hooks_dir = os.path.join('/', 'opt', 'anabot-hooks', event)
    for hook in os.listdir(hooks_dir):
        yield os.path.join(hooks_dir, hook)

def _run_hooks(hooks, chroot=None, preexec_fn=None):
    preexec = preexec_fn
    if chroot is not None:
        def tmp_preexec():
            if preexec_fn is not None:
                preexec_fn()
            os.chroot(chroot)
        preexec = tmp_preexec
    for hook in hooks:
        exec_path = hook
        if chroot is not None:
            new_dir = os.path.join(chroot, 'tmp')
            shutil.copy(hook, new_dir)
            exec_path = os.path.join(new_dir, os.path.basename(hook))
        os.chmod(exec_path, stat.S_IEXEC)
        p = subprocess.Popen([exec_path], preexec_fn=preexec)
        p.wait()
        if chroot is not None:
            os.unlink(exec_path)

def run_prehooks():
    _run_hooks(_hooks('pre'))

def run_postnochroothooks():
    _run_hooks(_hooks('post-nochroot'))

def run_posthooks():
    _run_hooks(_hooks('post'), chroot='/mnt/sysimage')
