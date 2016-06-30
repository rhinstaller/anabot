from anabot.preprocessor.variables import set_variable

with open('/proc/cmdline') as cmdline:
    items = cmdline.read().split()
    if 'anabot.beta' in items:
        set_variable('beta', True)
