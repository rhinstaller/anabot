# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

import os, shutil, subprocess, stat

def _hooks(event):
    hooks_dir = os.path.join('/', 'opt', 'anabot-hooks', event)
    for hook in sorted(os.listdir(hooks_dir)):
        yield os.path.join(hooks_dir, hook)

def _run_hooks(hooks, chroot=None, preexec_fn=None):
    for hook in hooks:
        _run_hook(hook, chroot, preexec_fn)

def _run_hook(hook, chroot=None, preexec_fn=None):
    preexec = preexec_fn
    if chroot is not None:
        def tmp_preexec():
            if preexec_fn is not None:
                preexec_fn()
            os.chroot(chroot)
        preexec = tmp_preexec
    exec_path = hook
    os.chmod(exec_path, stat.S_IEXEC)
    if chroot is not None:
        new_path = os.path.join(chroot, 'tmp', os.path.basename(hook))
        shutil.copy(hook, new_path)
        exec_path = os.path.join('/', 'tmp', os.path.basename(hook))
        logger.debug("Copying hook for chroot to: %s", new_path)
        logger.debug("Running hook (in chroot %s): %s", chroot, exec_path)
    else:
        logger.debug("Running hook: %s", exec_path)
    p = subprocess.Popen([exec_path], preexec_fn=preexec)
    p.wait()
    if chroot is not None:
        logger.debug("Removing hook from chroot: %s", new_path)
        os.unlink(new_path)

def run_prehooks():
    _run_hooks(_hooks('pre'))

def run_posthooks():
    def prio_cmp(x, y):
        return cmp(os.path.basename(x), os.path.basename(y))
    nochroots = list(_hooks('post-nochroot'))[::-1]
    chroots = list(_hooks('post'))[::-1]
    while len(chroots) > 0 or len(nochroots) > 0:
        if len(chroots) <= 0:
            _run_hook(nochroots.pop())
            continue
        if len(nochroots) <= 0:
            _run_hook(chroots.pop(), chroot='/mnt/sysimage')
            continue
        if prio_cmp(chroots[-1], nochroots[-1]) < 0:
            _run_hook(chroots.pop(), chroot='/mnt/sysimage')
        else:
            _run_hook(nochroots.pop())
