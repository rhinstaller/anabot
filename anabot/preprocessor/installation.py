import logging

logger = logging.getLogger('anabot.preprocessor')

import re

from .decorators import replace, default
from .functions import load_snippet, has_property, pop_property, copy_content
from .defaults import delete_element

@replace("/installation")
def replace_installation(element):
    if len(element.xpathEval('./welcome')) == 0:
        new_welcome = element.addChild(load_snippet("/installation/welcome", element, tag_name='_default_for'))
        first_el = element.xpathEval("./*")[0]
        if first_el != new_welcome:
            first_el.addPrevSibling(new_welcome)
        replace_welcome(new_welcome, element)
    if len(element.xpathEval('./hub')) == 0:
        new_hub = element.addChild(load_snippet("/installation/hub", element, tag_name='_default_for'))
        welcome_el = element.xpathEval("./*")[0]
        welcome_el.addNextSibling(new_hub)
        replace_hub(new_hub, element)
    if len(element.xpathEval('./configuration')) == 0:
        new_conf = element.addChild(load_snippet("/installation/configuration", element, tag_name='_default_for'))
        replace_configuration(new_conf, element)

@replace("/installation/welcome")
def replace_welcome(element, default_for=None):
    if default_for is None:
        default_for = element
    lang_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")
    lang_prop = pop_property(element, "language")
    if lang_prop is not None:
        new = load_snippet("/installation/welcome@language", element, True)
        copy_content(new, element)
        match = lang_re.match(lang_prop.content)
        lang = match.group("lang")
        element.xpathEval("./language")[0].setProp("value", lang)
        loc = match.group("loc")
        element.xpathEval("./locality")[0].setProp("value", loc)

@replace("/installation/hub")
def replace_hub(element, default_for=None):
    if default_for is None:
        default_for = element
    if len(element.xpathEval('./partitioning')) == 0:
        new = load_snippet("/installation/hub/autopart", default_for, tag_name="_default_for")
        element.addChild(new)

@replace("/installation/hub/autopart")
def replace_autopart(element, default_for=None):
    new = load_snippet("/installation/hub/autopart", element)
    element.replaceNode(new)

@replace("/installation/configuration")
def replace_configuration(element, default_for=None):
    if default_for is None:
        default_for = element
    if len(element.xpathEval("./root_password")) == 0:
        new = load_snippet("/installation/configuration/root", default_for, tag_name="_default_for")
        element.addChild(new)

@replace("/installation/configuration/root")
def replace_rootpw(element):
    new = load_snippet("/installation/configuration/root", element)
    element.replaceNode(new)
    password = element.xpathEval("./@password")[0].content
    new.xpathEval("./password")[0].setProp("value", password)
    new.xpathEval("./confirm_password")[0].setProp("value", password)

@replace("/installation/configuration/user")
def replace_user(element):
    delete_element(element)
