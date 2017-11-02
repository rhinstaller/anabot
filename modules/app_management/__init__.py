import os, subprocess, shlex

from anabot.runtime.hooks import register_preexec_hook, register_postexec_hook
from anabot.variables import get_variable
from anabot import config

def find_tested_app(atk_appname, atk_min_children=1, search_attempts=1, wait_between_attempts=1):
    import dogtail.utils
    dogtail.utils.enableA11y()
    import dogtail.tree
    from dogtail.predicate import GenericPredicate
    from dogtail.utils import sleep
    while search_attempts > 0:
        applications = dogtail.tree.root.findChildren(
            GenericPredicate(roleName="application", name=atk_appname),
            recursive=False,
        )
        for app in applications:
            if app.childCount >= atk_min_children:
                return app
        sleep(wait_between_attempts)
        search_attempts = search_attempts - 1
    return None

@register_preexec_hook(35)
def start_application():
    exe = get_variable('app_name', default=None)
    if exe is None:
        return
    cmd = [exe]
    cmd += shlex.split(get_variable('app_params', default=''))
    subprocess.Popen(cmd)

@register_preexec_hook(99)
def wait_for_application():
    atk_app_name = config.get_option('atk_app_name')
    min_children = int(config.get_option('atk_min_children'))
    app = find_tested_app(atk_app_name, min_children, search_attempts = 2, wait_between_attempts = 20)
    if app is None:
        raise Exception('Cannot find tested application')

@register_postexec_hook(10)
def kill_application():
    # TODO
    pass
