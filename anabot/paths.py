import sys, os
anabot_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# modules paths
teres_path = os.path.join(anabot_root, 'teres')
dogtail_path = os.path.join(anabot_root, 'lib/python2.7/site-packages')

# configuration paths
profiles_path = os.path.join(anabot_root, 'profiles')
defauls_path = os.path.join(profiles_path, 'default.ini')

# modules path
modules_path = os.path.join(anabot_root, 'modules')

# set sys.path
#   anabot path
sys.path.append(anabot_root)
#   dogtail path
# it has to be added after preexec hooks are run
#sys.path.append(dogtail_path)
#   teres path
sys.path.append(teres_path)
#   add modules path
sys.path.append(modules_path)
