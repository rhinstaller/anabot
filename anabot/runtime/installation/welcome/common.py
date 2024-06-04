import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check
from anabot.runtime.functions import getnode, getselected
from anabot.runtime.translate import set_languages_by_name

def set_language(local_node):
    #locales = getnode(local_node, "table", "Locales", visible=None)
    locales = getnode(local_node, "table", visible=None)
    language = getselected(locales, visible=None)[0].name
    set_languages_by_name(language)
    logger.info("Setting translator to: %s", language)
