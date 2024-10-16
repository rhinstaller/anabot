import os
import sys
import re

import teres
reporter = teres.Reporter.get_reporter()

from anabot.runtime.hooks import register_post_hook
sys.path.append(os.path.join(os.path.dirname(__file__), 'pngs2apng'))
import pngs2apng
from anabot.conditions import is_distro_version_ge
import logging

screenshot_dir = '/var/run/anabot'
screenshot_re = re.compile('[0-9]+-screenshot.png')
target_name = 'progress.apng'
target_path = os.path.join(screenshot_dir, target_name)

@register_post_hook(80)
def make_slideshow_from_screenshots():
    # Temporarily disabled on RHEL-10 and Fedora 40+ because of broken screenshot
    # functionality in dogtail - to be removed when RHEL-62420 is fixed.
    if is_distro_version_ge('rhel', 10) or is_distro_version_ge('fedora', 40):
        logger = logging.getLogger("anabot")
        logger.info("No screenshots available with Wayland, slideshow won't be generated.")
        return
    inputs = []
    for filename in sorted(os.listdir(screenshot_dir)):
        if screenshot_re.match(filename):
            inputs.append(os.path.join(screenshot_dir, filename))
    pngs2apng.pngs2apng(target_path, *inputs)
    reporter.send_file(target_path)
