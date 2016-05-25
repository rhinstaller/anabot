# -*- coding: utf-8 -*-

import urllib2
import libxml2

DEFAULT_COMPS_PATH = "/tmp/yum.cache/anaconda/gen/comps.xml"
_current_comps = None

def reload_comps(path=None):
    global _current_comps
    if path is None:
        path = DEFAULT_COMPS_PATH
    _current_comps = Comps(path)

def get_comps():
    if _current_comps is None:
        reload_comps()
    return _current_comps

class Comps(object):
    doc = None
    root = None

    def __init__(self, path):
        self.doc = libxml2.parseFile(path)
        self.root = self.doc.getRootElement()

    def env_list(self):
        xpath = '/comps/environment/id/text()'
        return [x.content for x in self.root.xpathEval(xpath)]

    def groups_list(self, env):
        xpath = '/comps/environment[id/text() = "%s"]/optionlist/groupid/text()' % env
        candidates = [x.content for x in self.root.xpathEval(xpath)]
        # shown are those that are visible and have non-zero count of
        # non-optional packages
        common_xpath = '/comps/group[uservisible/text() = "true" and count(packagelist/packagereq[@type != "optional"])]/id/text()'
        common_candidates = [x.content for x in self.root.xpathEval(common_xpath)]
        return candidates + common_candidates

    def tr_env(self, env_id, languages):
        for lang in languages:
            xpath = '/comps/environment[id/text() = "%s"]/name[@xml:lang="%s"]/text()' % (env_id, lang)
            try:
                return self.root.xpathEval(xpath)[0].content
            except IndexError:
                pass
        xpath = '/comps/environment[id/text() = "%s"]/name[not(@xml:lang)]/text()' % env_id
        try:
            return self.root.xpathEval(xpath)[0].content
        except IndexError:
            return None

    def tr_env_rev(self, env_name, languages):
        for lang in languages:
            xpath = '/comps/environment[name[@xml:lang="%s"]/text()="%s"]/id/text()' % (lang, env_name)
            try:
                return self.root.xpathEval(xpath)[0].content
            except IndexError:
                pass
        xpath = '/comps/environment[name[not(@xml:lang)]/text()="%s"]/id/text()' % env_name
        try:
            return self.root.xpathEval(xpath)[0].content
        except IndexError:
            return None

    def tr_env_desc(self, env_id, languages):
        for lang in languages:
            xpath = '/comps/environment[id/text() = "%s"]/description[@xml:lang="%s"]/text()' % (env_id, lang)
            try:
                return self.root.xpathEval(xpath)[0].content
            except IndexError:
                pass
        xpath = '/comps/environment[id/text() = "%s"]/description[not(@xml:lang)]/text()' % env_id
        try:
            return self.root.xpathEval(xpath)[0].content
        except IndexError:
            return None

    def tr_group(self, group_id, languages):
        for lang in languages:
            xpath = '/comps/group[id/text() = "%s"]/name[@xml:lang="%s"]/text()' % (group_id, lang)
            try:
                return self.root.xpathEval(xpath)[0].content
            except IndexError:
                pass
        xpath = '/comps/group[id/text() = "%s"]/name[not(@xml:lang)]/text()' % group_id
        try:
            return self.root.xpathEval(xpath)[0].content
        except IndexError:
            return None

    def tr_group_desc(self, group_id, languages):
        for lang in languages:
            xpath = '/comps/group[id/text() = "%s"]/description[@xml:lang="%s"]/text()' % (group_id, lang)
            try:
                return self.root.xpathEval(xpath)[0].content
            except IndexError:
                pass
        xpath = '/comps/group[id/text() = "%s"]/description[not(@xml:lang)]/text()' % group_id
        try:
            return self.root.xpathEval(xpath)[0].content
        except IndexError:
            return None
