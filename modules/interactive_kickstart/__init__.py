from anabot.runtime.variables import set_variable

if 'ks=' in open('/proc/cmdline').read():
    set_variable('interactive_kickstart', True)
else:
    set_variable('interactive_kickstart', False)
