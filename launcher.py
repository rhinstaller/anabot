#!/usr/bin/python

import sys, os
import logging
from logging.handlers import SysLogHandler
from anabot import config
from anabot.variables import set_variable

def show_help():
    print '%s profile_name recipe_url [varname=value[,varname=value]]' % sys.argv[0]

try:
    profile_name = sys.argv[1]
except IndexError as e:
    show_help()
    sys.exit(2)

anabot_vars = {}
for arg in sys.argv[2:]:
    (name, value) = arg.split('=',1)
    set_variable(name, value)

config.init_config(profile_name)

# start logging and reporting
logger = logging.getLogger('anabot')
logger.setLevel(config.get_option('log_level'))
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler(config.get_option('log_file')))
syslog = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_LOCAL3)
syslog.setFormatter(logging.Formatter(config.get_option('log_format')))

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

import teres
import teres.handlers
reporter = teres.Reporter.get_reporter()
test_log_handler = logging.FileHandler("/var/log/anabot-test.log")
reporter.add_handler(teres.handlers.LoggingHandler('anabot.test',
                                                   test_log_handler,
                                                   dest=None))

from anabot.paths import profiles_path, anabot_root
from anabot.preprocessor import preprocess
from anabot.runtime.hooks import register_executable_hooks, run_preexechooks

# propagate some config values as environment variables
os.environ['ANABOT_PROFILE'] = profile_name
os.environ['ANABOT_BASEDIR' ] = anabot_root

options_to_export = {
    # option_name: env_variable,
    'x_display': 'DISPLAY',
    'log_file': 'ANABOT_CONFIG_LOG_FILE',
    'hooks': 'ANABOT_CONFIG_HOOKS',
}

for option in options_to_export.keys():
    env_name = options_to_export[option]
    if not os.environ.has_key(env_name):
        value = config.get_option(option)
        if value is not None:
            os.environ[env_name] = value

logger.debug('Registering hooks for profile %s', profile_name)
hook_paths = [os.path.join(profile_name, 'hooks'),]
for opt in 'default_hooks', 'hooks':
    p = config.get_option(opt)
    if (p is not None) and (p != ''):
        hook_paths.append(os.path.join(profiles_path, p))

for p in set(hook_paths):
    if os.path.isdir(p):
        register_executable_hooks(p)

# import modules - also registers modules hooks
from modules import import_modules
import_modules()

# run preexec_hooks
logger.debug('Running preexec hooks')
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
           "/var/run/anabot/final-recipe.xml",
           application=config.get_option('preprocessor_profile'))

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
app_name = config.get_option('atk_app_name')
min_children = config.get_option('atk_min_children')

from anabot.paths import dogtail_path
sys.path.append(dogtail_path)
from anabot.runtime.run_test import run_test

run_test("/var/run/anabot/final-recipe.xml", appname=app_name, children_required=min_children)
