import os, subprocess, shlex

from anabot.runtime.hooks import register_preexec_hook
from anabot.variables import get_variable

@register_preexec_hook(35)
def start_application():
    exe = get_variable('app_name', default=None)
    if exe is None:
        return
    cmd = [exe]
    cmd += shlex.split(get_variable('app_params', default=''))
    subprocess.Popen(cmd)
