import os, sys, logging
logger = logging.getLogger('anabot')
from importlib import import_module
from anabot.paths import modules_path
from anabot.exceptions import UnrelatedException
from anabot.runtime.hooks import register_executable_hooks

def import_modules():
    if os.path.isdir(modules_path):
        for module_name in sorted(os.listdir(modules_path)):
            if not os.path.isdir(modules_path + '/' + module_name):
                continue
            register_module_hooks = True
            try:
                logger.debug("Importing anabot module: %s", module_name)
                import_module(module_name)
                logger.debug("Imported anabot module: %s", module_name)
            except ImportError:
                logger.debug("Import failed for anabot module: %s", module_name)
            except UnrelatedException:
                logger.debug("Module reports, that it's not related for current environment")
                register_module_hooks = False
            finally:
                if register_module_hooks:
                    # register module's executable hooks
                    register_executable_hooks(modules_path + '/' + module_name)

