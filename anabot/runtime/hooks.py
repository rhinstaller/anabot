# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')
import teres
reporter = teres.Reporter.get_reporter()

import os, shutil, subprocess, stat
import functools
from anabot import config, variables

_hooks = {
    'preexec': [],
    'pre': [],
    'post': [],
    'postexec': [],
}

def _is_hook_registered(hook, hook_list):
    p = hook[0]
    f = hook[1]
    if isinstance(f, functools.partial):
        for prio, func in hook_list:
            if isinstance(func, functools.partial):
                if (p == prio) and \
                   (f.func == func.func) and \
                   (f.args == func.args) and \
                   (f.keywords == func.keywords):
                    return True
        return False
    else:
        return hook in hook_list

def format_partial(f):
    if not isinstance(f, functools.partial):
        return f
    fmt = '<functools.partial(%(func)s, args=%(args)s, kwargs=%(kwargs)s) object at 0x%(address)x>'
    return fmt % {
        'func' : f.func,
        'args' : f.args,
        'kwargs' : f.keywords,
        'address' : id(f),
    }

def register_hook(hook_type, priority=None, func=None):
    '''registers hook function in internal list
    can be used as a decorator'''
    logger.debug('Registering hook %s, %s %s', priority, hook_type, func)
    def decorator(f):
        new_hook = (priority, f)
        if not _is_hook_registered(new_hook, _hooks[hook_type]):
            _hooks[hook_type].append(new_hook)
        return f
    if func is not None:
        return decorator(func)
    return decorator

def register_preexec_hook(priority=None, func=None):
    return register_hook('preexec', priority, func)

def register_pre_hook(priority=None, func=None):
    return register_hook('pre', priority, func)

def register_post_hook(priority=None, func=None):
    return register_hook('post', priority, func)

def register_postexec_hook(priority=None, func=None):
    return register_hook('postexec', priority, func)

def _register_hook_executable(exe_path=None):
    logger.debug('Registering executable hook %s', exe_path)
    basename = os.path.basename(exe_path)
    # cut off .suffix (it can be .hook but in theory anything else
    hookname = basename.rsplit('.', 1)[0]
    # TODO check filename format
    parts = hookname.split('-')
    try:
        prio = int(parts[0])
        hook_type = parts[-1]
        chroot_required = True
        if hook_type == 'nochroot':
            chroot_required = False
            hook_type = parts[-2]
        if hook_type in ('preexec', 'pre'):
            chroot_required = False
        chroot = None
        if chroot_required:
            chroot = config.get_option('chroot')
        register_hook(hook_type, prio, functools.partial(_run_executable_hook, executable=exe_path, chroot=chroot))
    except ValueError:
        logger.warning('Ignoring %s - cannot get prio - bad filename format', exe_path)

def register_executable_hooks(path=None):
    logger.debug('Adding hooks from path %s', path)
    for hook in os.listdir(path):
        if hook.endswith('.hook'):
            _register_hook_executable(os.path.join(path, hook))

def _run_executable_hook(executable=None, chroot=None, preexec_fn=None):
    preexec = preexec_fn
    if chroot is not None:
        def tmp_preexec():
            if preexec_fn is not None:
                preexec_fn()
            os.chroot(chroot)
        preexec = tmp_preexec
    hook = executable
    os.chmod(executable, stat.S_IEXEC)
    if chroot is not None:
        chrooted_path = config.get_option('chroot_hook_path')
        new_path = os.path.join(
            chroot, chrooted_path.lstrip(os.path.sep), os.path.basename(hook)
        )
        shutil.copy(hook, new_path)
        exec_path = os.path.join('/', chrooted_path, os.path.basename(hook))
        logger.debug("Copying hook for chroot to: %s", new_path)
        logger.debug("Running hook (in chroot %s): %s", chroot, exec_path)
    else:
        exec_path = hook
        logger.debug("Running hook: %s", exec_path)
    p = subprocess.Popen([exec_path], preexec_fn=preexec)
    p.wait()
    logger.debug("Hook exited with conde: %d", p.returncode)
    if chroot is not None:
        logger.debug("Removing hook from chroot: %s", new_path)
        os.unlink(new_path)
    # executable hooks needs some method to set env and variables back in main process
    vars_file = config.get_option('hook_update_vars_file')
    env_file = config.get_option('hook_update_env_file')
    if chroot is not None:
        vars_file = os.path.join('/', chrooted_path, vars_file)
        env_file = os.path.join('/', chrooted_path, env_file)
    _merge_hook_data(vars_file, variables.set_variable)
    _merge_hook_data(env_file, variables.set_env_variable)

def _none_is_greater_cmp(x, y):
    # all hooks should be registered as python functions
    if x == y: return 0
    if x is None: return 1
    if y is None: return -1
    if x > y: return 1
    if x < y: return -1
    raise Exception('Comparison unexpected state')

def _first_key_none_is_greater(x, y):
    return _none_is_greater_cmp(x[0], y[0])

def _run_hooks(hook_type, preexec_fn=None):
    hook_list = sorted(
        _hooks[hook_type],
        key=functools.cmp_to_key(_first_key_none_is_greater),
        reverse=True
    )
    while len(hook_list) > 0:
        prio, hook = hook_list.pop()
        try:
            reporter.log_debug("Running hook: %s" % format_partial(hook))
            hook()
        except Exception as e:
            reporter.log_error("Hook raised exception: %s" % e)
    _hooks[hook_type] = hook_list

def run_preexechooks():
    _run_hooks('preexec')

def run_prehooks():
    _run_hooks('pre')

def run_posthooks():
    _run_hooks('post')

def run_postexechooks():
    _run_hooks('postexec')

def _merge_hook_data(datafile, set_func):
    '''
parse datafile for key=value lines and call set_func(key, value)
    '''
    if not os.path.exists(datafile):
        return False
    with open(datafile, 'r') as data:
        for l in data:
            try:
                l = l.rstrip('\n')
                name, value = l.split('=', 1)
                set_func(name, value)
            except ValueError:
                logger.warning("Ignoring line - cannot get key/value pair '%s'", l)
    os.unlink(datafile)
