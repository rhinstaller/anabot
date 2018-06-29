import teres
import re
import logging
import six

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import get_attr, getnode, getnodes
from anabot.runtime.translate import tr as translate
from anabot.runtime.errors import TimeoutError
from anabot.runtime.actionresult import ActionResultPass as Pass
from anabot.runtime.actionresult import ActionResultFail as Fail
from anabot.runtime.actionresult import NotFoundResult as NotFound

logger = logging.getLogger('anabot')
reporter = teres.Reporter.get_reporter()

_local_path = '/installation/welcome/storage_error_dialog'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)
STORAGE_ERR_LABEL = "" + \
"There is a problem with your existing storage configuration: %(errortxt)s\n" + \
"\n" + \
"You must resolve this matter before the installation can proceed. There is a " + \
"shell available for use which you can access by pressing ctrl-alt-f1 and " + \
"then ctrl-b 2.\n" + \
"\n" + \
"Once you have resolved the issue you can retry the storage scan. If you do " + \
"not fix it you will have to exit the installer."


def get_retry_button(dialog):
    try:
        return getnode(dialog, "push button", translate("_Retry"))
    except TimeoutError:
        try:
            return getnode(dialog, "push button", "Retry")
        except TimeoutError:
            return None
        return None


def get_exit_button(dialog):
    try:
        return getnode(dialog, "push button", translate("_Exit Installer"))
    except TimeoutError:
        try:
            return getnode(dialog, "push button", "Exit Installer")
        except TimeoutError:
            return None
        return None


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

        translated = translate(STORAGE_ERR_LABEL)
        translated_re = translated % {"errortxt": "(.*)"}
        mo = re.match(translated_re, six.u(label.text))

        # Workaround for bug 1420226
        original_re = STORAGE_ERR_LABEL % {"errortxt": "(.*)"}
        mo_original = re.match(original_re, label.text)

        if mo_original is not None and translated != STORAGE_ERR_LABEL:
            reporter.log_fail(
                "The storage error dialog isn't traslated. See bug 1420226")
            mo = mo_original

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
            retry_button = get_retry_button(dialog)
            if retry_button is None:
                return NotFound("retry button", where="error storage dialog")
            retry_button.click()
        elif action == "exit":
            exit_button = get_exit_button(dialog)
            if exit_button is None:
                return NotFound("exit button", where="error storage dialog")
            exit_button.click()
        else:
            pass

        return Pass()

    return NotFound("storage error dialog")
