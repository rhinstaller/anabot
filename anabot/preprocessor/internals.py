import logging

logger = logging.getLogger('anabot.preprocessor')

import re

from . import EASY_NS_URIS
from .decorators import _REPLACES, _DEFAULTS
from .functions import tag_elements

DROP_NS_RE = re.compile(r'/[^:/ ]+:')
DROP_NS = lambda x: DROP_NS_RE.sub('/', x)
DROP_NUM_RE = re.compile(r'\[[0-9]+\]')
DROP_NUM = lambda x: DROP_NUM_RE.sub('', x)

def do_replace(element):
    node_path = DROP_NS(DROP_NUM(element.nodePath()))
    _REPLACES.get(node_path, _REPLACES[None])(element)
    element.setNs(None)

def remove_easy_namespace(document):
    for element in document.xpathEval('//*'):
        for EASY_NS_URI in EASY_NS_URIS:
            element.removeNsDef(EASY_NS_URI)
