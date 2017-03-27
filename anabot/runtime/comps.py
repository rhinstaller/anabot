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

    def defined_groups(self):
        defined_xpath = '/comps/group/id/text()'
        return [x.content for x in self.root.xpathEval(defined_xpath)]

    def visible_groups(self):
        visible_xpath = '/comps/group[uservisible/text() != "false"]/id/text()'
        return [x.content for x in self.root.xpathEval(visible_xpath)]

    def non_optional_non_conditional_groups(self):
        xpath = '/comps/group[count(packagelist/packagereq[@type != "optional" and @type != "conditional"]) != 0]/id/text()'
        return [x.content for x in self.root.xpathEval(xpath)]

    def _filter_defined_groups(self, candidates):
        defined = self.defined_groups()
        return [x for x in candidates if x in defined]

    def _filter_visible_groups(self, candidates):
        visible = self.visible_groups()
        return [x for x in candidates if x in visible]

    def _filter_non_optional_non_conditional_groups(self, candidates):
        non_optional_non_conditional = self.non_optional_non_conditional_groups()
        return [x for x in candidates if x in non_optional_non_conditional]

    def groups_list(self, env):
        xpath = '/comps/environment[id/text() = "%s"]/optionlist/groupid/text()' % env
        candidates = [x.content for x in self.root.xpathEval(xpath)]
        # shown are also those that are visible
        candidates += self.visible_groups()
        # filter out those groups that are only referenced, but not defined
        candidates = self._filter_defined_groups(candidates)
        # filter out those groups that contain only optional and/or conditional
        # packages
        candidates = self._filter_non_optional_non_conditional_groups(candidates)
        return candidates

    def mandatory_groups_list(self, env):
        xpath = '/comps/environment[id/text() = "%s"]/grouplist/groupid/text()' % env
        candidates = [x.content for x in self.root.xpathEval(xpath)]
        # filter out those groups that are only referenced, but not defined
        candidates = self._filter_defined_groups(candidates)
        return candidates

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

    def tr_group_rev(self, group_name, languages):
        for lang in languages:
            xpath = '/comps/group[name[@xml:lang="%s"]/text()="%s"]/id/text()' % (lang, group_name)
            try:
                return self.root.xpathEval(xpath)[0].content
            except IndexError:
                pass
        xpath = '/comps/group[name[not(@xml:lang)]/text()="%s"]/id/text()' % group_name
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
