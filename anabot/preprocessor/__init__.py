import libxml2
import sys, re
import os.path

import logging

logger = logging.getLogger('anabot.preprocessor')
logger.addHandler(logging.NullHandler())

from .decorators import replace, default
from .internals import copy_replace_tree, place_defaults

from . import defaults, installation

def preprocess(input_path='-', output_path='-', application="installation"):
    # https://mail.gnome.org/archives/xml/2004-November/msg00008.html
    oldblankmode = libxml2.keepBlanksDefault(0) # very very ugly hack

    if input_path == '-':
        indoc = libxml2.parseDoc(sys.stdin.read())
    else:
        indoc = libxml2.parseFile(input_path)
    outdoc = indoc.copyDoc(False)
    copy_replace_tree(indoc, outdoc, True)
    place_defaults(outdoc.getRootElement(), application)
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
