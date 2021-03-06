import libxml2
import sys, re
import os.path

import logging

logger = logging.getLogger('anabot.preprocessor')
logger.addHandler(logging.NullHandler()) # pylint: disable=no-member

EASY_NS_URIS = [
    'http://example.com/path/anabot/easy',
    'http://fedoraproject.org/anaconda/anabot/recipe/tiny/1'
]

from .decorators import replace
from .internals import do_replace, remove_easy_namespace

from . import defaults, installation

def preprocess(input_path='-', output_path='-', application="installation"):
    # https://mail.gnome.org/archives/xml/2004-November/msg00008.html
    oldblankmode = libxml2.keepBlanksDefault(0) # very very ugly hack

    if input_path == '-':
        indoc = libxml2.parseDoc(sys.stdin.read())
    else:
        indoc = libxml2.parseFile(input_path)
    outdoc = indoc.copyDoc(True)
    for EASY_NS_URI in EASY_NS_URIS:
        xpath = outdoc.xpathNewContext()
        xpath.xpathRegisterNs('ez', EASY_NS_URI)
        easies = [(e, e.nodePath()) for e in xpath.xpathEval('//ez:*')]
        if easies:
            break
    for element, node_path in sorted(easies, key=lambda x: x[1], reverse=True):
        do_replace(element)
    remove_easy_namespace(outdoc)
    if output_path == '-':
        sys.stdout.write(outdoc.serialize(format=1))
    else:
        with open(output_path + '.orig', 'w') as outfile_orig:
            indoc.dump(outfile_orig)
        with open(output_path, 'w') as outfile:
            outfile.write(outdoc.serialize(format=1))
    indoc.freeDoc()
    outdoc.freeDoc()

    libxml2.keepBlanksDefault(oldblankmode) # cleanup very very ugly hack
