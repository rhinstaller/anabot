# -*- coding: utf-8 -*-

import libxml2
from glob import glob
from anabot.runtime.functions import merge_lists
from anabot.conditions import is_distro_version_ge

DEFAULT_COMPS_SEARCH_PATHS = [
    "/tmp/yum.cache/anaconda/gen/comps.xml",
    "/tmp/dnf.cache/*/repodata/gen/groups.xml"
]
_current_comps = None

def reload_comps(paths=[]):
    global _current_comps
    final_paths = []
    if len(paths) == 0:
        paths = DEFAULT_COMPS_SEARCH_PATHS
    for search_path in paths:
        # get all of the existing comps files paths
        for path in glob(search_path):
            final_paths.append(path)
    if len(final_paths) == 0:
        raise Exception("Couldn't find any comps file(s) in the following search paths: " + ", ".join(paths))
    _current_comps = CompsBundle(final_paths)

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

    def non_conditional_groups(self):
        non_conditional_xpath = '/comps/group[count(packagelist/packagereq[@type != "conditional"]) != 0]/id/text()'
        return [x.content for x in self.root.xpathEval(non_conditional_xpath)]

    def _filter_defined_groups(self, candidates):
        defined = self.defined_groups()
        return [x for x in candidates if x in defined]

    def _filter_visible_groups(self, candidates):
        visible = self.visible_groups()
        return [x for x in candidates if x in visible]

    def _filter_non_conditional_groups(self, candidates):
        non_conditional = self.non_conditional_groups()
        return [x for x in candidates if x in non_conditional]

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
        # packages (RHEL-7) or conditional packages (RHEL-8)
        if is_distro_version_ge("rhel", 8):
            candidates = self._filter_non_conditional_groups(candidates)
        else:
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
            # return empty string, since this group probably doesn't have any
            # description at all
            return ""

class CompsBundle(object):
    _comps_list = []

    def __init__(self, paths):
        self._comps_list = [Comps(path) for path in paths]

    def env_list(self):
        env_lists = [comps.env_list() for comps in self._comps_list]
        return merge_lists(env_lists)

    def defined_groups(self):
        groups_lists = [comps.defined_groups() for comps in self._comps_list]
        return merge_lists(groups_lists)

    def visible_groups(self):
        groups_lists = [comps.visible_groups() for comps in self._comps_list]
        return merge_lists(groups_lists)

    def non_optional_non_conditional_groups(self):
        groups_lists = [comps.non_optional_non_conditional_groups() for comps in self._comps_list]
        return merge_lists(groups_lists)

    def non_conditional_groups(self):
        groups_lists = [comps.non_conditional_groups() for comps in self._comps_list]
        return merge_lists(groups_lists)

    def groups_list(self, env):
        groups_lists = [comps.groups_list(env) for comps in self._comps_list]
        return merge_lists(groups_lists)

    def mandatory_groups_list(self, env):
        groups_lists = [comps.mandatory_groups_list(env) for comps in self._comps_list]
        return merge_lists(groups_lists)

    def tr_env(self, env_id, languages):
        for comps in self._comps_list:
            if env_id in comps.env_list():
                return comps.tr_env(env_id, languages)
        return None

    def tr_env_rev(self, env_name, languages):
        for comps in self._comps_list:
            env_id = comps.tr_env_rev(env_name, languages)
            if env_id is not None:
                return env_id
        return None

    def tr_env_desc(self, env_id, languages):
        for comps in self._comps_list:
            if env_id in comps.env_list():
                return comps.tr_env_desc(env_id, languages)
        return None

    def tr_group(self, group_id, languages):
        for comps in self._comps_list:
            group_name = comps.tr_group(group_id, languages)
            if group_name is not None:
                return group_name
        return None

    def tr_group_rev(self, group_name, languages):
        for comps in self._comps_list:
            group_id = comps.tr_group_rev(group_name, languages)
            if group_id is not None:
                return group_id
        return None

    def tr_group_desc(self, group_id, languages):
        for comps in self._comps_list:
            group_desc = comps.tr_group_desc(group_id, languages)
            if group_desc != "":
                return group_desc
        return ""
