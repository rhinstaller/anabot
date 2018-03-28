import datetime
import time
import re
import six

def from_now(seconds):
    """Just return 2 datetime objects: now(), now()+seconds"""
    starttime = datetime.datetime.now()
    endtime = starttime + datetime.timedelta(seconds=seconds)
    return starttime, endtime

def wait_for_line(filename, expr, timeout):
    """
    Wait until there's expr matching line in the desired file.
    The timeout argument is in seconds and have to be set.
    There is no way of setting infinite timeout.
    """
    if isinstance(expr, six.string_types):
        expr = re.compile(expr)
    with open(filename) as watchfile:
        starttime, endtime = from_now(timeout)
        while True:
            now = datetime.datetime.now()
            if now < starttime:
                # damn you anaconda for changing system time
                starttime, endtime = from_now(timeout)
            if now > endtime:
                return False
            while True: # damn you python for not having nice for
                line = watchfile.readline()
                if line == '':
                    break
                if expr.match(line):
                    return True
            time.sleep(1)
