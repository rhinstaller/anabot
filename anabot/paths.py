import sys, os
anabot_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# modules paths
teres_path = anabot_root + '/teres'
dogtail_path = anabot_root + '/lib/python2.7/site-packages'

# configuration paths
defauls_path = anabot_root + '/profiles/default.ini'
profiles_path = anabot_root + '/profiles'

# modules path
modules_path = anabot_root + '/modules'

# set sys.path
#   anabot path
sys.path.append(anabot_root)
#   dogtail path
sys.path.append(dogtail_path)
#   teres path
sys.path.append(teres_path)
#   add modules path
sys.path.append(modules_path)
