import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.default import default_handler
from anabot.runtime.functions import get_attr, getnode
from anabot.runtime.translate import tr



_local_path = '/initial_setup/license'
handle_act = lambda x: handle_action(_local_path + x)
handle_chck = lambda x: handle_check(_local_path + x)


@handle_act('')
def base_handler(element, app_node, local_node):
    license = getnode(app_node, "spoke selector", tr("LICENSE INFORMATION"))
    license.click()
    license_label = getnode(app_node, "label", tr("License Agreement:"))
    license_panel = license_label.parent.parent
    license_text = getnode(license_panel, 'text', '')
    default_handler(element, app_node, license_panel.parent)

@handle_act('/eula')
def empty_handler(element, app_node, local_node):
    pass

@handle_chck('/eula')
def eula_chck(element, app_node, local_node):
    def reformat_eula(file_name):
        eula_file = file(file_name)
        # reformat stored eula according to initial setup
        fobj_lines = eula_file.xreadlines()
        stored_eula = ""
        firstline = True
        for line in fobj_lines:
            stripped_line = line.strip()
            if stripped_line:
                if firstline:
                    stored_eula = stripped_line
                    firstline = False
                else:
                    stored_eula += " " + stripped_line
            else:
                stored_eula += "\n\n"
        eula_file.close()
        return stored_eula

    license_file = "/usr/share/redhat-release/EULA"
    license_label = getnode(app_node, "label", tr("License Agreement:"))
    license_panel = license_label.parent.parent
    license_text = getnode(license_panel, 'text', '')
    displayed_eula = license_text.text
    return displayed_eula == reformat_eula(license_file)
    

@handle_act('/accept_license')
def accept_license_handler(element, app_node, local_node):
    license_checkbox = getnode(app_node, "check box", tr("I accept the license agreement."))
    should_check = get_attr(element, 'checked')
    if should_check == 'yes':
        if not license_checkbox.checked:
            license_checkbox.click()
    else:
        if license_checkbox.checked:
            license_checkbox.click()

@handle_chck('/accept_license')
def accept_license_check(element, app_node, local_node):
    license_checkbox = getnode(app_node, "check box", tr("I accept the license agreement."))
    return license_checkbox.checked

@handle_act('/done')
def done_handler(element, app_node, local_node):
    done_button = getnode(local_node, "push button", tr("_Done", False))
    done_button.click()



