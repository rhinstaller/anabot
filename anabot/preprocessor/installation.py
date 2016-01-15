import logging

logger = logging.getLogger('anabot.preprocessor')

import re

from .decorators import replace, default
from .functions import load_snippet, has_property, pop_property

@replace("/installation/welcome")
def replace_welcome(original):
    lang_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")
    if has_property(original, "language"):
        new = load_snippet("/installation/welcome@language", original, True)
    else:
        new = original.copyNode(False)

    lang_prop = pop_property(new, "language")
    if lang_prop is not None:
        match = lang_re.match(lang_prop.content)
        lang = match.group("lang")
        new.xpathEval("./language")[0].setProp("value", lang)
        loc = match.group("loc")
        new.xpathEval("./locality")[0].setProp("value", loc)
    return new

@replace("/installation/hub/autopart")
def replace_autopart(original):
    return load_snippet("/installation/hub/autopart", original)

@replace("/installation/configuration/root")
def replace_rootpw(original):
    new = load_snippet("/installation/configuration/root", original)
    password = original.xpathEval("./@password")[0].content
    new.xpathEval("./password")[0].setProp("value", password)
    new.xpathEval("./confirm_password")[0].setProp("value", password)
    return new

@replace("/installation/configuration/user")
def replace_user(original):
    pass

@default("installation", "/installation/welcome")
def default_welcome(root):
    # need to place welcome before hub (hub < welcome)
    hub = root.xpathEval("/installation/hub")[0]
    new = load_snippet("/installation/welcome")
    hub.addPrevSibling(new)
    return new

@default("installation", "/installation/hub")
def default_hub(root):
    # need to place hub before configuration (configuration < hub)
    configuration = root.xpathEval("/installation/configuration")[0]
    new = root.newChild(None, "hub", None)
    configuration.addPrevSibling(new)
    return new

@default("installation", "/installation/hub/partitioning")
def default_partitioning(root):
    new = load_snippet("/installation/hub/autopart")
    root.xpathEval("/installation/hub")[0].addChild(new)
    return new

@default("installation", "/installation/configuration")
def default_configuration(root):
    new = root.newChild(None, "configuration", None)
    return new

@default("installation", "/installation/configuration/root_password")
def default_root_password(root):
    new = load_snippet("/installation/configuration/root_password")
    root.xpathEval("/installation/configuration")[0].addChild(new)
    return new
