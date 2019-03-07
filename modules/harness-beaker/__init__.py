# -*- coding: utf-8 -*-

""" This module adds initializes ThinBkrHandler which is then registered with
Reporter instance."""

import os
import teres
import teres.bkr_handlers
from anabot.exceptions import UnrelatedException

beaker_lab_controller = os.getenv("LAB_CONTROLLER",
                                  os.getenv("BEAKER_LAB_CONTROLLER"))
beaker_recipe_id = os.getenv("RECIPEID")
if beaker_lab_controller is None:
    raise UnrelatedException("Beaker lab controller environmet variable not set.")
if beaker_recipe_id is None:
    raise UnrelatedException("Beaker recipeid environmet variable not set.")

# Set up beaker handler
beaker_lab_controller_url = "http://" + beaker_lab_controller + ":8000/"

rep = teres.Reporter.get_reporter()
hnd = teres.bkr_handlers.ThinBkrHandler(
    recipe_id=beaker_recipe_id,
    lab_controller_url=beaker_lab_controller_url,
    report_overall="./anabot/done",
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
    teres.bkr_handlers.SUBTASK_RESULT:"./anabot",
    teres.bkr_handlers.DEFAULT_LOG_DEST:True
}
rep.log_pass("Anabot started", flags=flags)
