python_sources = [
  '__init__.py',
  'ponytail.py',
]

python3 = import('python3')
pythondir = join_paths(prefix, python3.sysconfig_path('purelib'))
install_data(python_sources, install_dir: pythondir + '/ponytail')
