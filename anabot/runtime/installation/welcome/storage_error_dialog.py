from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import get_attr, getnode, getnodes
from anabot.runtime.translate import tr as translate
from anabot.runtime.errors import TimeoutError
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound

import re
import logging
logger = logging.getLogger('anabot')

_local_path = '/installation/welcome/storage_error_dialog'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
STORAGE_ERR_LABEL = "There is a problem with your existing storage configuration: %(errortxt)s\n"


@handle_act('')
def storage_error_dialog_handler(element, app_node, local_node):
    err_type = get_attr(element, "err_type")
    # The action can be one of these ""
    action = get_attr(element, "action")

    for dialog in getnodes(app_node, "dialog"):
        try:
            label = getnode(dialog, "label")
        except TimeoutError:
            return NotFound("error dialog")

        msg = label.text.split("\n")[0] + '\n'
        translated = translate(STORAGE_ERR_LABEL)
        translated_re = translated % {"errortxt": "(.*)"}

        mo = re.match(translated_re, msg)
        if mo is None:
            logger.info("Wrong dialog found.")
            continue

        blivet_err = mo.group(1)
        logger.info("Blivet error: %s", blivet_err)

        if err_type is not None and blivet_err.startswith(err_type):
            pass
        else:
            return Fail("Different error message encountered.")

        if action == "retry":
            try:
                retry = getnode(dialog, "push button", translate("Retry"))
            except TimeoutError:
                return NotFound("retry button")
            retry.click()
        elif action == "exit":
            try:
                exit = getnode(dialog, "push button",
                               translate("Exit Installer"))
            except TimeoutError:
                return NotFound("exit button")
            exit.click()
        else:
            pass

        return Pass()

    return NotFound("storage error dialog")
