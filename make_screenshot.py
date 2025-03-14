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
from struct import pack, unpack
from dasbus.connection import SessionMessageBus
import dogtail, dogtail.utils, dogtail.config # pylint: disable=import-error

session_type_file = "/run/anabot/session_type"

def main(path):
    try:
        with open(session_type_file, "r") as st:
            session_type = st.read()
    except FileNotFoundError:
        print(f"make_screenshot: session type file '{session_type_file}' "
            "not found, assuming wayland session")
        session_type = "wayland"
    if session_type not in ("x11", "wayland"):
        print(f"make_screenshot: unknown session type '{session_type}'!")
        sys.exit(1)

    if session_type == "x11":
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":1"
        dogtail.utils.enableA11y()
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)
        if len(dirname) == 0:
            dirname = os.getcwd()
        dogtail.config.config.scratchDir = dirname
        dogtail.utils.screenshot(filename, timeStamp=False)
    elif session_type == "wayland":
        if os.path.exists(path):
            os.unlink(path)

        bus = SessionMessageBus()
        proxy = bus.get_proxy("org.gnome.Shell.Screenshot", "/org/gnome/Shell/Screenshot")
        proxy.Screenshot(True, False, path)
        # The original file contains information about date/time, so two subsequent files aren't
        # binary identical even if they contain the same image, so we need to fix it.
        prune_png_chunks(path)

def prune_png_chunks(path):
    """
    Remove all but required data chunks from a PNG file.
    This is necessary to ensure that two files containing the
    same image will be binary identical, thus allowing for an
    easy deduplication.
    """

    # PNG file structure: https://en.wikipedia.org/wiki/PNG#File_format
    PNG_HEADER_LEN = 8
    IHDR_LEN = 4 + 4 + 13 + 4 # length, type, data, CRC

    with open(path, 'rb') as f:
        new_png = f.read(PNG_HEADER_LEN + IHDR_LEN)
        chunk_type = None
        while chunk_type != b'IEND':
            length = unpack('!I', f.read(4))[0]
            chunk_type = f.read(4)
            chunk_data = f.read(length)
            chunk_crc = f.read(4)
            # retain only critical chunks (although PLTE is likely not present)
            if chunk_type in (b'IDAT', b'PLTE'):
                new_png += pack('!I', length)   # chunk length
                new_png += chunk_type           # chunk type (IDAT)
                new_png += chunk_data           # chunk data
                new_png += chunk_crc            # CRC
        # write IEND chunk as the last one
        new_png += pack('!I', 0)                # IEND length = 0
        new_png += chunk_type
        new_png += chunk_crc

    with open(path, 'wb') as f:
        f.write(new_png)

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
