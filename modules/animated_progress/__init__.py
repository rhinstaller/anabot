import os
import sys
import re

import teres
reporter = teres.Reporter.get_reporter()

from anabot.runtime.hooks import register_post_hook
sys.path.append(os.path.join(os.path.dirname(__file__), 'pngs2apng'))
import pngs2apng

screenshot_dir = '/var/run/anabot'
screenshot_re = re.compile('[0-9]+-screenshot.png')
target_name = 'progress.apng'
target_path = os.path.join(screenshot_dir, target_name)

@register_post_hook(80)
def make_slideshow_from_screenshots():
    inputs = []
    for filename in sorted(os.listdir(screenshot_dir)):
        if screenshot_re.match(filename):
            inputs.append(os.path.join(screenshot_dir, filename))
    pngs2apng.pngs2apng(target_path, *inputs)
    reporter.send_file(target_path)
