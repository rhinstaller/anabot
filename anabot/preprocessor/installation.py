import logging

logger = logging.getLogger('anabot.preprocessor')

import re

from .decorators import replace, default
from .functions import load_snippet, has_property, pop_property
from .defaults import delete_element

@replace("/installation")
def replace_installation(element):
    if len(element.xpathEval('./welcome')) == 0:
        new_welcome = element.addChild(load_snippet("/installation/welcome", element, tag_name='_default_for'))
        first_el = element.xpathEval("./*")[0]
        if first_el != new_welcome:
            first_el.addPrevSibling(new_welcome)
    if len(element.xpathEval('./hub')) == 0:
        new_hub = element.addChild(load_snippet("/installation/hub", element, tag_name='_default_for'))
        welcome_el = element.xpathEval("./*")[0]
        welcome_el.addNextSibling(new_hub)
    if len(element.xpathEval('./configuration')) == 0:
        new_conf = element.addChild(load_snippet("/installation/configuration", element, tag_name='_default_for'))

    return element

@replace("/installation/welcome")
def replace_welcome(element):
    lang_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")
    lang_prop = pop_property(element, "language")
    if lang_prop is not None:
        new = load_snippet("/installation/welcome@language", element, True)
        element.replaceNode(new)
        match = lang_re.match(lang_prop.content)
        lang = match.group("lang")
        new.xpathEval("./language")[0].setProp("value", lang)
        loc = match.group("loc")
        new.xpathEval("./locality")[0].setProp("value", loc)
        return new
    return element

@replace("/installation/hub/autopart")
def replace_autopart(element):
    new = load_snippet("/installation/hub/autopart", element)
    element.replaceNode(new)
    return new

@replace("/installation/configuration/root")
def replace_rootpw(element):
    new = load_snippet("/installation/configuration/root", element)
    element.replaceNode(new)
    password = element.xpathEval("./@password")[0].content
    new.xpathEval("./password")[0].setProp("value", password)
    new.xpathEval("./confirm_password")[0].setProp("value", password)
    return new

@replace("/installation/configuration/user")
def replace_user(element):
    delete_element(element)
