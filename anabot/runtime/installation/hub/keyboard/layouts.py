# -*- coding: utf-8 -*-

from anabot.runtime.translate import lang_tr, keyboard_tr, active_languages

class Layouts(object):
    __instance = None

    @staticmethod
    def get_instance():
        if Layouts.__instance is None:
            Layouts.__instance = Layouts()
        return Layouts.__instance

    def __init__(self):
        super(Layouts, self).__init__()
        self.__last_langs = None

    @property
    def dirty(self):
        return self.__last_langs != active_languages()

    def clean(self):
        self.__last_langs = active_languages()

    def reload(self):
        if not self.dirty:
            return
        self.__layouts = {}
        from gi.repository import Gtk, GdkX11, Xkl # pylint: disable=no-name-in-module
        display = GdkX11.x11_get_default_xdisplay()
        engine = Xkl.Engine.get_instance(display)
        configreg = Xkl.ConfigRegistry.get_instance(engine)
        configreg.load(False)
        configreg.foreach_language(self.__language_variants, None)
        configreg.foreach_country(self.__country_variants, None)
        self.clean()

    def __language_variants(self, c_reg, item, user_data=None):
        lang_name = item.get_name()
        lang_desc = item.get_description()
        c_reg.foreach_language_variant(
            lang_name,
            self.__language_subvariants,
            lang_desc
        )

    def __language_subvariants(self, c_reg, item, subitem, lang):
        if subitem:
            target = u"%s (%s)" % (item.get_name(), subitem.get_name())
            text = u"%s (%s)" % (
                lang_tr(lang).capitalize(),
                keyboard_tr(subitem.get_description())
            )
        else:
            target = u"%s" % item.get_name()
            text = u"%s (%s)" % (
                lang_tr(lang).capitalize(),
                keyboard_tr(item.get_description())
            )
        self.__layouts[target] = text

    def __country_variants(self, c_reg, item, user_data=None):
        country_name = item.get_name()
        country_desc = item.get_description()
        c_reg.foreach_country_variant(
            country_name,
            self.__country_subvariants,
            country_desc
        )

    def __country_subvariants(self, c_reg, item, subitem, country):
        # country should be translated, but isn't - Anaconda bug!
        if subitem:
            target = u"%s (%s)" % (item.get_name(), subitem.get_name())
            text = u"%s (%s)" % (country, keyboard_tr(subitem.get_description()))
        else:
            target = u"%s" % item.get_name()
            text = u"%s (%s)" % (country, keyboard_tr(item.get_description()))
        if target not in self.__layouts:
            self.__layouts[target] = text

    def __getitem__(self, key):
        self.reload()
        return self.__layouts[key]

    def get(self, key, default=None):
        self.reload()
        return self.__layouts.get(key, default)

    def __iter__(self):
        self.reload()
        return self.__layouts.iteritems()

def layout_name(intext, default=None):
    return Layouts.get_instance().get(intext, default)

def layout_id(outtext, default=None):
    for layout_id, layout_name in self:
        if layout_name == outtext:
            return layout_id
    return default
