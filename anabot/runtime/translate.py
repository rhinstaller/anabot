#!/bin/python

import re
import gettext
import langtable # pylint: disable=import-error
from .comps import get_comps
__translate = None
__translate_keyboard = None
__translate_lang = None
__translate_country = None
__languages = None
__oscap_translate = None
__locality = None
__locality_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")

def active_languages():
    return __languages

def set_languages_by_name(locality):
    match = __locality_re.match(locality)
    lang = match.group("lang")
    set_languages([langtable.languageId(locality),
                   langtable.languageId(lang),
                   "en"])

def set_languages(languages):
    global __translate, __languages, __oscap_translate, __translate_keyboard, __translate_lang, __translate_coutntry
    __translate = gettext.translation('anaconda', languages=languages,
                                      fallback=True)
    __translate_keyboard = gettext.translation('xkeyboard-config',
                                               languages=languages,
                                               fallback=True)
    __translate_lang = gettext.translation('iso_639',
                                           languages=languages,
                                           fallback=True)
    __translate_country = gettext.translation('iso_3166',
                                              languages=languages,
                                              fallback=True)
    __languages = languages
    __oscap_translate = gettext.translation('oscap-anaconda-addon',
                                            languages=languages,
                                            fallback=True)

def _tr(translate, intext, drop_underscore=True, context=None):
    if not isinstance(intext, (str, unicode)):
        raise TypeError("Can't translate object of type %s." % type(intext))

    # Some translations have context but python gettext doesn't support
    # contexts. There is workaround for this issue:
    # https://bugs.python.org/issue2504#msg106121
    if context is not None:
        intext = context + "\x04" + intext
    outtext = translate.ugettext(intext)
    # drop context if there is no translation
    if context is not None and outtext == intext:
        outtext = outtext[len(context)+1:]
    if drop_underscore:
        outtext = outtext.replace('_', '', 1)
    return outtext

def tr(intext, drop_underscore=True, context=None):
    return _tr(__translate, intext, drop_underscore, context)

def oscap_tr(intext, drop_underscore=True, context=None):
    return _tr(__oscap_translate, intext, drop_underscore, context)


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

def datetime_tr(name):
    for lang in __languages:
        translated = langtable.timezone_name(timezoneId=name,
                                             languageIdQuery=lang)
        if translated != name:
            return translated
    return name

def keyboard_tr(intext):
    if isinstance(intext, unicode):
        outtext = __translate_keyboard.ugettext(intext)
    else:
        outtext = __translate_keyboard.ugettext(intext.decode('utf-8'))
    return outtext

def lang_tr(intext):
    if isinstance(intext, unicode):
        outtext = __translate_lang.ugettext(intext)
    else:
        outtext = __translate_lang.ugettext(intext.decode('utf-8'))
    return outtext

def country_tr(intext):
    # not used yet, but we can keep it for future
    if isinstance(intext, unicode):
        outtext = __translate_country.ugettext(intext)
    else:
        outtext = __translate_country.ugettext(intext.decode('utf-8'))
    return outtext

set_languages(['en'])
