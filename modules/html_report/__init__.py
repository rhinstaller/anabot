import StringIO

from anabot.runtime.hooks import register_post_hook
import teres
import teres.bkr_handlers # we should get rid of this in future

LINE_FORMAT='<li class="result_%(result_name)s">[ %(result_name)s ] %(msg)s</li>\n'
IMG_FORMAT='<li><img src="./%(logname)s" /></li>\n'
FILE_FORMAT='<li><a href="./%(logname)s">FILE: %(logname)s</a></li>\n'
HEAD="""<html>
  <head>
    <title>Anabot HTML report</title>
    <style>
.result_PASS {
  color: green;
}
.result_FAIL {
  color: red;
}
.result_ERROR {
  font-weight: bold;
  color: red;
}
    </style>
  </head>
  <body>
    <ul>
"""
TAIL="""
    </ul>
  </body>
</html>
"""

def _rec2dict(record):
    return {
        'result' : record.result,
        'result_name' : teres.result_to_name(record.result),
        'msg' : record.msg,
        'logfile' : record.logfile,
        'logname' : record.logname,
        'flags' : record.flags,
    }

class HTMLReportHandler(teres.Handler):
    def __init__(self):
        self._done = False
        self._data = StringIO.StringIO()
        self._add_head()
        super(HTMLReportHandler, self).__init__()

    def _emit_log(self, record):
        if self._done:
            return
        self._data.write(LINE_FORMAT % _rec2dict(record))

    def _emit_file(self, record):
        if self._done:
            return
        if record.logname == 'record.html':
            return
        # I know, I know
        if isinstance(record.logfile, str) and record.logname is None:
            record.logname = teres.bkr_handlers._path_to_name(record.logfile)
        if record.logname is None:
            record.logname = record.logfile.name
        if record.logname == '<fdopen>':
            return
        if record.logname.endswith('last-screenshot.png'):
            return
        record_dict = _rec2dict(record)
        if record.logname.endswith('.png'):
            self._data.write(IMG_FORMAT % record_dict)
        else:
            self._data.write(FILE_FORMAT % record_dict)

    def _add_head(self):
        self._data.write(HEAD)

    def _add_tail(self):
        self._data.write(TAIL)

    def make_report(self):
        self._done = True
        self._add_tail()
        teres.Reporter.get_reporter().send_file(self._data, 'report.html')

    def close(self):
        pass

handler = HTMLReportHandler()
teres.Reporter.get_reporter().add_handler(handler)

register_post_hook(99, handler.make_report)
