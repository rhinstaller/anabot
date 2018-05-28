#!/usr/bin/python2 -i

import sys
import os
import pickle
import urllib2

def list_dirs(path):
    return [
        os.path.join(path, x)
        for x in os.listdir(path)
        if os.path.isdir(os.path.join(path, x))
    ]

# Add dogtail import path
for d in list_dirs('dogtail'):
    sys.path.append(d)
# Add teres import path
sys.path.append('teres')
# Add modules import path
sys.path.append('modules')

def main(source=None):
    if source is None:
        print 'usage:'
        print './load_traceback.py /path/to/traceback.dump'
        print 'or:'
        print './load_traceback.py http://url/to/traceback.dump'
        print
        print 'You see shell, but dump is not loaded!'
        return None
    if os.path.exists(source):
        source = open(source)
    else:
        source = urllib2.urlopen(source)
    return pickle.load(source)

if __name__ == "__main__":
    import pprint
    print 'Note (if you see traceback about dogtail):'
    print 'Dogtail has to be in import path or unpacked in dogtail directory'
    print
    print 'Here you have shell, with traceback dump available in dump variable'
    print "There's also pprint module imported for you already"
    dump = main(*sys.argv[1:])
