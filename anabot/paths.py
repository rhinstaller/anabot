import sys, os
anabot_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# modules paths
teres_path = os.path.join(anabot_root, 'teres')
libs_path = os.path.join(
    anabot_root,
    'lib/python%(major)s.%(minor)s/site-packages' % {
        'major': sys.version_info.major,
        'minor': sys.version_info.minor,
    }
)

# configuration paths
profiles_path = os.path.join(anabot_root, 'profiles')
defauls_path = os.path.join(profiles_path, 'default.ini')

# modules path
modules_path = os.path.join(anabot_root, 'modules')

# set sys.path
#   anabot path
sys.path.append(anabot_root)
#   additional libs path (we don't want to mess the system, so we use our
#   site-packages dir)
sys.path.append(libs_path)
#   add modules path
sys.path.append(modules_path)
# utility to take screenshot
screenshot_executable = os.path.join(anabot_root, 'make_screenshot')
