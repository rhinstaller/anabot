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

def tr(intext, drop_underscore=True, context=None):
    # Some translations have context but python gettext doesn't support
    # contexts. There is workaround for this issue:
    # https://bugs.python.org/issue2504#msg106121
    if context is not None:
        intext = context + "\x04" + intext
    outtext = __translate.ugettext(intext)
    # drop context if there is no translation
    if outtext == intext:
        outtext = outtext[len(context)+1:]
    if drop_underscore:
        outtext = outtext.replace('_', '', 1)
    return outtext

set_languages(['en'])
