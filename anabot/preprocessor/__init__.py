import libxml2
import sys, re
import os.path

REPLACES = {}
DEFAULTS = {}

def replace(node_path):
    def decorator(func):
        REPLACES[node_path] = func
        return func
    return decorator

def default(node_path):
    def decorator(func):
        DEFAULTS[node_path] = func
        return func
    return decorator

def load_snippet(name, original_element = None, copy_attrs = True, tag_name="_replacing"):
    tdoc = libxml2.parseFile(os.path.dirname(__file__) + '/snippets' + name + ".xml")
    doc = tdoc.copyDoc(True) # cannot modify document unless it's copied
    new = doc.getRootElement()
    if copy_attrs:
        for prop in original_element.xpathEval("./@*"):
            new.addChild(prop.copyProp(None))
    if original_element is not None:
        tag_elements(doc, original_element, tag_name)
    tdoc.freeDoc()
    return new

def has_property(element, prop_name):
    return len(element.xpathEval("./@" + prop_name)) == 1

def pop_property(element, prop_name):
    try:
        prop = element.xpathEval("./@" + prop_name)[0].copyNode(True)
    except IndexError:
        return None
    element.unsetProp(prop_name)
    return prop

def tag_elements(new, orig, tag_name="_replacing"):
    tag_element(new, orig, tag_name)
    for child in new.xpathEval("./*"):
        tag_elements(child, orig, tag_name)

def tag_element(new, orig, tag_name="_replacing"):
    #new.newProp(tag_name, orig.nodePath())
    pass

def pop_child(element, child_name):
    pass

@replace(None)
def copy(element):
    new = element.copyNode(False)
    for prop in element.xpathEval("./@*"):
        new.addChild(prop.copyProp(None))
    return new

@replace("/installation/welcome")
def replace_welcome(original):
    lang_re = re.compile(r"(?P<lang>[^(]*) (?:\((?P<loc>[^)]*)\))?")
    if has_property(original, "language"):
        new = load_snippet("/installation/welcome@language", original)
    else:
        new = original.copyNode(False)

    lang_prop = pop_property(new, "language")
    if lang_prop is not None:
        match = lang_re.match(lang_prop.content)
        lang = match.group("lang")
        new.xpathEval("./language")[0].setProp("value", lang)
        loc = match.group("loc")
        new.xpathEval("./locality")[0].setProp("value", loc)
    return new

def copy_replace_tree(src_element, dst_parent, root=False):
    for child in src_element.xpathEval("./*"):
        if child.nodePath() in REPLACES:
            new_child = REPLACES[child.nodePath()](child)
        else:
            new_child = REPLACES[None](child)
        if root:
            dst_parent.setRootElement(new_child)
        else:
            dst_parent.addChild(new_child)
        copy_replace_tree(child, new_child)

def preprocess(input_path = '-', output_path = '-', debug = False):
    # https://mail.gnome.org/archives/xml/2004-November/msg00008.html
    oldblankmode = libxml2.keepBlanksDefault(0) # very very ugly hack

    indoc = libxml2.parseFile(input_path)
    outdoc = indoc.copyDoc(False)
    copy_replace_tree(indoc, outdoc, True)
    with open(output_path + '.orig', 'w') as outfile_orig:
        indoc.dump(outfile_orig)
    with open(output_path, 'w') as outfile:
        outfile.write(outdoc.serialize(format=1))
    if debug:
        print outdoc.serialize(format=1)
    indoc.freeDoc()
    outdoc.freeDoc()

    libxml2.keepBlanksDefault(oldblankmode) # cleanup very very ugly hack
