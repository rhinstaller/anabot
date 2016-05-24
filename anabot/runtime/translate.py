#!/bin/python

import re
import gettext
import langtable # pylint: disable=import-error
from .comps import get_comps
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
    global __translate, __languages
    __translate = gettext.translation('anaconda', languages=languages,
                                      fallback=True)
    __languages = languages

def tr(intext, drop_underscore=True, context=None):
    # Some translations have context but python gettext doesn't support
    # contexts. There is workaround for this issue:
    # https://bugs.python.org/issue2504#msg106121
    if context is not None:
        intext = context + "\x04" + intext
    outtext = __translate.ugettext(intext)
    # drop context if there is no translation
    if context is not None and outtext == intext:
        outtext = outtext[len(context)+1:]
    if drop_underscore:
        outtext = outtext.replace('_', '', 1)
    return outtext


def comps_tr_env(env_id):
    comps = get_comps()
    return comps.tr_env(env_id, __languages)

def comps_tr_env_rev(env_id):
    comps = get_comps()
    return comps.tr_env_rev(env_id, __languages)

def comps_tr_env_desc(env_id):
    comps = get_comps()
    return comps.tr_env_desc(env_id, __languages)

def comps_tr_group(group_id):
    comps = get_comps()
    return comps.tr_group(group_id, __languages)

def comps_tr_group_desc(group_id):
    comps = get_comps()
    return comps.tr_group_desc(group_id, __languages)

set_languages(['en'])
