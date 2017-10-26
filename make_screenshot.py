import sys, os
import site
import platform
my_path = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(
    os.path.join(
        my_path,
        'lib/python%(major)d.%(minor)d/site-packages' % {
            'major': sys.version_info.major,
            'minor': sys.version_info.minor,
        }
    )
)
site.addsitedir(
    os.path.join(
        my_path,
        'lib/%(arch)s/python%(major)s.%(minor)s/site-packages' % {
            'arch': platform.machine(),
            'major': sys.version_info.major,
            'minor': sys.version_info.minor,
        }
    )
)
import dogtail, dogtail.utils, dogtail.config

def main(path):
    dogtail.utils.enableA11y()
    filename = os.path.basename(path)
    dirname = os.path.dirname(path)
    if len(dirname) == 0:
        dirname = os.getcwd()
    dogtail.config.config.scratchDir = dirname
    dogtail.utils.screenshot(filename, timeStamp=False)

if __name__ == "__main__":
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":1"
    sys.exit(main(*sys.argv[1:]))
