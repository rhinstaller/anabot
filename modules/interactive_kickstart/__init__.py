from anabot.variables import set_variable

if 'ks=' in open('/proc/cmdline').read():
    set_variable('interactive_kickstart', '1')
else:
    set_variable('interactive_kickstart', '0')
