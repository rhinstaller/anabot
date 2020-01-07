import shlex

from anabot.variables import set_variable

# defaults
set_variable('interactive_kickstart', '0')

cmdline = open('/proc/cmdline').read()
for arg in shlex.split(cmdline):
    try:
        key, value = arg.split('=', 1)
        # kwarg is here
        elif key in ('inst.ks', 'ks'):
            set_variable('interactive_kickstart', '1')
    except ValueError:
        # arg is here
        pass
