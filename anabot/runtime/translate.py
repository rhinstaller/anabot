#!/bin/python

import re
import six
import gettext
import langtable # pylint: disable=import-error
from .comps import get_comps
import logging
__translate = None
__translate_keyboard = None
__translate_lang = None
__translate_country = None
__languages = None
__oscap_translate = None
__gtk_translate = None
__locality = None
__locality_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")
logger = logging.getLogger('anabot')

def active_languages():
    return __languages

def set_languages_by_name(locality):
    match = __locality_re.match(locality)
    lang = match.group("lang")
    locality_language_id = langtable.languageId(locality)

    # Chinese language id is reported as zh_XXXX_YY, but for the translation we can only use zh_YY (e. g. zh_CN)
    chinese = re.match("(zh).*(..)", locality_language_id)
    if chinese:
        updated_locality_language_id = "_".join(chinese.groups())
        logger.info("Chinese was selected, using '%s' instead of '%s." %
            (updated_locality_language_id, locality_language_id)
        )
        locality_language_id = updated_locality_language_id

    set_languages([locality_language_id,
                   langtable.languageId(lang),
                   "en"])

def set_languages(languages):
    global __translate, __languages, __oscap_translate, __translate_keyboard, __translate_lang, __translate_country, __gtk_translate
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
    __gtk_translate = gettext.translation('gtk30',
                                          languages=languages,
                                          fallback=True)

def _tr(translate, intext, drop_underscore=True, context=None):
    if not isinstance(intext, six.string_types):
        raise TypeError("Can't translate object of type %s." % type(intext))

    # Some translations have context but python gettext doesn't support
    # contexts. There is workaround for this issue:
    # https://bugs.python.org/issue2504#msg106121
    if context is not None:
        intext = context + "\x04" + intext
    outtext = translate.gettext(intext)
    # drop context if there is no translation
    if context is not None and outtext == intext:
        outtext = outtext[len(context)+1:]
    if drop_underscore:
        outtext = outtext.replace('_', '', 1)
    return six.u(outtext)

def tr(intext, drop_underscore=True, context=None):
    return _tr(__translate, intext, drop_underscore, context)

def oscap_tr(intext, drop_underscore=True, context=None):
    return _tr(__oscap_translate, intext, drop_underscore, context)

def gtk_tr(intext, drop_underscore=True, context=None):
    return _tr(__gtk_translate, intext, drop_underscore, context)

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

def comps_tr_group_rev(group_name):
    comps = get_comps()
    return comps.tr_group_rev(group_name, __languages)

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
    if isinstance(intext, six.text_type):
        outtext = __translate_keyboard.gettext(intext)
    else:
        outtext = __translate_keyboard.gettext(intext.decode('utf-8'))
    return outtext

def lang_tr(intext):
    if isinstance(intext, six.text_type):
        outtext = __translate_lang.gettext(intext)
    else:
        outtext = __translate_lang.gettext(intext.decode('utf-8'))
    return outtext

def country_tr(intext):
    # not used yet, but we can keep it for future
    if isinstance(intext, six.text_type):
        outtext = __translate_country.gettext(intext)
    else:
        outtext = __translate_country.gettext(intext.decode('utf-8'))
    return outtext

set_languages(['en'])
