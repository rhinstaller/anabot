# -*- coding: utf-8 -*-

""" This module adds initializes ThinBkrHandler which is then registered with
Reporter instance."""

import os
import re
import subprocess
try:
    # python3
    from urllib.request import urlopen
    import ssl
    # disable SSL verification when running in beaker
    ssl._create_default_https_context = ssl._create_unverified_context
except ImportError:
    # python2
    from urllib import urlopen
import json
import time
import libxml2
import teres
import teres.bkr_handlers
from anabot.exceptions import UnrelatedException
from anabot.variables import set_variable, get_variable

BEAKER = "https://%s" % get_variable('beaker_hub_hostname')
with open('/proc/cmdline', 'r') as proc_cmdline:
    cmdline = proc_cmdline.read()

def http_get(url):
    urllib_obj = urlopen(url)
    if urllib_obj.getcode() != 200:
        print("Couldn't get URL:", url)
        raise Exception()
    return teres.make_text(urllib_obj.read())

def is_kickstart():
    # Parse recipe id from kernel cmdline.
    return 'ks=' in cmdline

def lab_controller_cmdline():
    try:
        return re.search(r'(?<=labcontroller=)([^\s]+)', cmdline).group(0)
    except AttributeError:
        return None

def lab_controller(system_fqdn):
    if lab_controller_cmdline() is not None:
        return lab_controller_cmdline()
    system_data = http_get("%s/systems/%s/" % (BEAKER, system_fqdn))
    system_data = json.loads(system_data)
    lab_controller_id = system_data['lab_controller_id']
    for lab_controller in system_data['possible_lab_controllers']:
        if lab_controller['id'] == lab_controller_id:
            return lab_controller['fqdn']
    # fallback, just try to use first one if none matches
    return system_data['possible_lab_controllers'][0]['fqdn']

def get_hostname(localhost="localhost", retries=10):
    for i in range(retries):
        hostname = teres.make_text(
            subprocess.check_output(["hostname"])
        ).strip()
        if hostname != localhost:
            break
        time.sleep(1)
    return hostname

def get_recipe_id():
    # when running in kickstart mode, recipeid may be in kickstart
    if is_kickstart():
        recipeid_re = re.compile(r'echo ([0-9]+) > /root/RECIPE.TXT')
        with open('/run/install/ks.cfg') as kickstart:
            for line in kickstart:
                stripped = line.strip()
                match = recipeid_re.match(stripped)
                if match is not None:
                    return match.group(1)
    # not running in kickstart mode, recipeid should be on kernel cmdline
    try:
        return re.search(r'(?<=recipeid=)([^\s]+)', cmdline).group(0)
    except AttributeError as err:
        raise UnrelatedException("Cannot find recipe id.")

def get_task_id(beaker_recipe):
    xpath = '/job/recipeSet/recipe/task[@status="Running" or @status="Waiting"]/@id'
    return beaker_recipe.xpathEval(xpath)[0].content

beaker_recipe_id = get_recipe_id()
os.environ['BEAKER_RECIPE_ID'] = beaker_recipe_id

# Get lab controller of the system.
hostname = get_hostname()
beaker_lab_controller = lab_controller(hostname)
os.environ["BEAKER_LAB_CONTROLLER"] = beaker_lab_controller

# Set up beaker handler
beaker_lab_controller_url = "http://" + beaker_lab_controller + ":8000/"

rep = teres.Reporter.get_reporter()
hnd = teres.bkr_handlers.ThinBkrHandler(
    recipe_id=beaker_recipe_id,
    lab_controller_url=beaker_lab_controller_url,
    report_overall="./reinstall/anabot/done",
)
debug_hnd = teres.bkr_handlers.ThinBkrHandler(
    recipe_id=beaker_recipe_id,
    lab_controller_url=beaker_lab_controller_url,
    result_level=teres.NONE,
    process_logs=False,
    task_log_name="debug-testout.log",
    disable_subtasks=True,
)

rep.add_handler(hnd)
rep.add_handler(debug_hnd)
flags = {
    teres.bkr_handlers.SUBTASK_RESULT:"./reinstall/anabot",
    teres.bkr_handlers.DEFAULT_LOG_DEST:True
}
rep.log_pass("Anabot started", flags=flags)

# Parse anabot recipe url from beaker recipe.
beaker_recipe_url = "http://" + beaker_lab_controller + ":8000/recipes/" + str(beaker_recipe_id) + "/"
beaker_recipe = http_get(beaker_recipe_url)
xml = libxml2.parseDoc(beaker_recipe)
task_id = get_task_id(xml)
os.environ['BEAKER_TASK_ID'] = task_id
def param_value(name, default=None, empty_default=True):
    param_xpath = '/job/recipeSet/recipe/task[@id="{}"]/params/param[@name="{}"]/@value'.format(task_id, name)
    try:
        value = xml.xpathEval(param_xpath)[0].content
        if empty_default and len(value) == 0:
            return default
        return value
    except IndexError:
        return default

anabot_recipe_url = param_value("ANABOT_RECIPE_URL")

rep.log_debug("Anabot recipe url is: {}".format(anabot_recipe_url))

# Store anabot recipe in correct place.
anabot_recipe_dir = "/var/run/anabot/"
anabot_recipe_path = anabot_recipe_dir + "raw-recipe.xml"
if not os.path.isdir(anabot_recipe_dir):
    os.makedirs(anabot_recipe_dir)

anabot_recipe = http_get(anabot_recipe_url)

try:
    with open(anabot_recipe_path, 'w') as output_file:
        output_file.write(anabot_recipe)
except IOError as err:
    rep.log_error("Could not write anabot recipe: {}".format(err))

# Is harness installation enabled? Default: yes
# If running kickstart installation harness should be in kickstat, so
# for those installations, default is no.
install_harness_default = "0" if is_kickstart() else "1"
install_harness = param_value("INSTALL_HARNESS", install_harness_default)
if install_harness != "1":
    os.environ["INSTALL_HARNESS"] = "0"
    rep.log_debug("Won't install nor configure harness after installation.")
else:
    os.environ["INSTALL_HARNESS"] = "1"
    rep.log_debug("Will install and configure harness after installation.")

# Should we install beakerlib?
install_beakerlib = param_value("INSTALL_BEAKERLIB", "0")
if install_beakerlib != "0":
    rep.log_debug("Adding beakerlib to install packages")
    install_packages = os.environ.get("INSTALL_PACKAGES", "")
    install_packages += " beakerlib beakerlib-redhat"
    os.environ["INSTALL_PACKAGES"] = install_packages
else:
    rep.log_debug("Not installing beakerlib")

# Is anaconda expected to be beta?
beta = param_value("BETA", "0")
if beta != "0":
    rep.log_debug("Setting preprocessor beta variable to True")
    set_variable("beta", "1")
else:
    rep.log_debug("BETA task param not found, empty or zero in beaker recipe")
