#!/bin/python

import re
import gettext
import langtable
__translate = None
__language = None
__locality = None
__locality_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")

def set_languages_by_name(locality):
    match = __locality_re.match(locality)
    lang = match.group("lang")
    set_languages([langtable.languageId(locality),
                   langtable.languageId(lang),
                   "en"])

def set_languages(languages):
    global __translate
    __translate = gettext.translation('anaconda', languages=languages,
                                      fallback=True)

def tr(intext):
    return __translate.ugettext(intext)

set_languages(['en'])
