from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import getnode, getselected
from anabot.runtime.translate import set_languages_by_name

def set_language(local_node):
    locales = getnode(local_node, "table", "Locales")
    set_languages_by_name(getselected(locales)[0].name)
