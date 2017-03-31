#!/usr/bin/python

import sys, os
from importlib import import_module
from ConfigParser import NoOptionError
from ConfigParser import RawConfigParser
import logging
from logging.handlers import SysLogHandler

def show_help():
    print '%s profile_name (recipe_url|recipe_file)' % sys.argv[0]

try:
    profile_name = sys.argv[1]
    recipe_url = sys.argv[2]
except IndexError as e:
    show_help()
    sys.exit(2)

# anabot path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# dogtail path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/python2.7/site-packages')
# teres path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/teres')


ini_path = os.path.dirname(os.path.abspath(__file__)) + '/profiles/' + profile_name + '.ini'
defaults_path = os.path.dirname(os.path.abspath(__file__)) + '/profiles/default.ini'
ini = RawConfigParser(allow_no_value=True)
loaded = ini.read([defaults_path, ini_path])

for p in (ini_path, defaults_path):
    if not p in loaded:
        raise Exception("Cannot load '%s'" % p)

# load config values
config = {
    'default_hooks': None,
    'hooks': None,
    'x_display': None,
    'atk_app_name': None,
    'atk_min_children': None,
    'log_format': None,
    'log_file': None,
    'log_level': None,
}

replacements = {
    'profile_name': profile_name,
}

for option in config.keys():
    try:
        value = ini.get(profile_name, option)
        try:
            config[option] = value % replacements
        except KeyError:
            config[option] = value
    except NoOptionError:
        pass

# set default values, modify values
log_level = config['log_level']
if log_level is None:
    config['log_level'] = logging.NOTSET
elif log_level == 'DEBUG':
    config['log_level'] = logging.DEBUG
elif log_level == 'INFO':
    config['log_level'] = logging.INFO
elif log_level == 'WARNING':
    config['log_level'] = logging.WARNING
elif log_level == 'ERROR':
    config['log_level'] = logging.ERROR
elif log_level == 'CRITICAL':
    config['log_level'] = logging.CRITICAL
else:
    raise Exception('Cannot set log level to %s' % log_level)

if config['log_file'] is None:
    raise Exception('Log file is not set')

if config['log_format'] is None:
    raise Exception('Log format is not set')

# start logging and reporting
logger = logging.getLogger('anabot')
logger.setLevel(config['log_level'])
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(config['log_file']))
syslog = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL3)
syslog.setFormatter(logging.Formatter(config['log_format']))

# virtio console - useful for debugging
VIRTIO_CONSOLE = '/dev/virtio-ports/com.redhat.anabot.0'
if os.path.exists(VIRTIO_CONSOLE):
    logger.addHandler(logging.FileHandler(VIRTIO_CONSOLE))
logger.addHandler(syslog)

# teres - connection with beaker
teres_logger = logging.getLogger("teres")
teres_logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("/var/log/anabot-teres.log"))
teres_stdout_handler = logging.StreamHandler(sys.stdout)
teres_stdout_handler.setFormatter(logging.Formatter("TERES: %(message)s"))
teres_logger.addHandler(teres_stdout_handler)
if os.environ.get('TERES_PATH'):
    sys.path.append(os.environ.get('TERES_PATH'))
import teres
import teres.handlers
reporter = teres.Reporter.get_reporter()
test_log_handler = logging.FileHandler("/var/log/anabot-test.log")
reporter.add_handler(teres.handlers.LoggingHandler('anabot.test',
                                                   test_log_handler,
                                                   dest=None))

from anabot.runtime.hooks import register_post_hook, register_preexec_hook, register_pre_hook
from anabot.runtime.hooks import run_preexechooks, exec_shellscript
from anabot.exceptions import UnrelatedException
from anabot.preprocessor import preprocess
from anabot.runtime import run_test

# propagate some config values as environment variables
os.environ['ANABOT_PROFILE'] = profile_name
os.environ['ANABOT_CONFIG_RECIPE'] = recipe_url

options_to_export = {
    # option_name: env_variable,
    'x_display': 'DISPLAY',
    'log_file': 'ANABOT_CONFIG_LOG_FILE',
    'hooks': 'ANABOT_CONFIG_HOOKS',
}

for option in options_to_export.keys():
    env_name = options_to_export[option]
    if not os.environ.has_key(env_name):
        value = config[option]
        if value is not None:
            os.environ[env_name] = value

# register hooks for profile
hook_types = ['preexec', 'pre', 'post', 'post-nochroot']

def register_hook_executable(hook_type, exe_path):
    logger.debug('HOOK: registering %s', exe_path)
    # hooks are sorted alphabetically so as prio we can use basename
    prio = os.path.basename(exe_path)
    if hook_type == 'preexec':
        register_preexec_hook(prio, lambda: exec_shellscript(exe_path))
    elif hook_type == 'pre':
        register_pre_hook(prio, lambda: exec_shellscript(exe_path))
    elif hook_type == 'post':
        register_post_hook(prio, lambda: exec_shellscript(exe_path))
    elif hook_type == 'post-chroot':
        # does it make sense to have different chroot for hooks?
        register_post_hook(prio, lambda: exec_shellscript(exe_path, chroot='/mnt/sysimage'))
    else:
        raise Exception("Unknown hook type '%s'" % hook_type)

def register_hooks(hooks_path):
    logger.debug('HOOK: processing path %s', hooks_path)
    for hook in os.listdir(hooks_path):
        hook_type = None
        for ht in hook_types:
            if hook.endswith(ht + '.hook'):
                hook_type = ht
                break
        if hook_type is not None:
            register_hook_executable(hook_type, hooks_path + '/' + hook)

logger.debug('HOOK: registering hooks for profile %s', profile_name)
profiles_path = os.path.dirname(os.path.abspath(__file__)) + '/profiles'
for p in set([config['default_hooks'], config['hooks'], profile_name + '/hooks']):
    if (p is not None) and (p != ''):
        hooks_path = profiles_path + '/' + p
        if os.path.isdir(hooks_path):
            register_hooks(hooks_path)

# import modules
modules_path = os.path.dirname(os.path.abspath(__file__)) + '/modules'
if os.path.isdir(modules_path):
    sys.path.append(modules_path)
    for module_name in sorted(os.listdir(modules_path)):
        try:
            logger.debug("Importing anabot module: %s", module_name)
            module = import_module(module_name)
            logger.debug("Imported anabot module: %s", module_name)
            # register module's executable hooks
            register_hooks(modules_path + '/' + module_name)
        except ImportError:
            logger.debug("Import failed for anabot module: %s", module_name)
        except UnrelatedException as e:
            logger.debug("Module reports, that it's not related for current environment")

# run preexec_hooks
logger.debug('HOOK: running preexec hooks')
run_preexechooks()

# check recipe
if not os.path.exists("/var/run/anabot/raw-recipe.xml"):
    reporter.log_error("No anabot recipe found!")
    reporter.test_end()
    raise Exception("No anabot recipe found!")

# log recipe
reporter.send_file("/var/run/anabot/raw-recipe.xml",
                   "raw-anabot-recipe.xml")

# TODO here should be validity check of raw recipe

# run preprocesor
if os.path.exists("/var/run/anabot/final-recipe.xml"):
    os.unlink("/var/run/anabot/final-recipe.xml")

preprocess("/var/run/anabot/raw-recipe.xml",
           "/var/run/anabot/final-recipe.xml")

# check final recipe
if not os.path.exists("/var/run/anabot/final-recipe.xml"):
    reporter.log_error("No final anabot recipe found!")
    reporter.test_end()
    raise Exception("No final anabot recipe found!")

# log final recipe
reporter.send_file("/var/run/anabot/final-recipe.xml",
                   "final-anabot-recipe.xml")

# TODO here should be validity check of final recipe

# finally process recipe
app_name = 'anaconda'
min_children = None
if config['atk_app_name'] is not None:
    app_name = config['atk_app_name']
if config['atk_min_children'] is not None:
    min_children = config['atk_min_children'] # will be used with subscription_manager_gui

run_test("/var/run/anabot/final-recipe.xml", appname=app_name)
