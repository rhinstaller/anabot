project('gnome-ponytail-daemon', 'c',
        version: '0.0.11',
        meson_version: '>= 0.40.0',
        default_options: ['warning_level=1',
                          'buildtype=debugoptimized'])

gnome = import('gnome')
glib_dep = dependency('glib-2.0')
gio_dep = dependency('gio-2.0')
gio_unix_dep = dependency('gio-unix-2.0')
libei_dep = dependency('libei-1.0', version : '>=1.0.0', required: false, fallback : ['libei', 'dep_libei'])
libxkbcommon_dep = dependency('xkbcommon', required: libei_dep.found())
systemd_dep = dependency('systemd')

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
dbusservicedir =  join_paths(datadir, 'dbus-1', 'services')

servicedir = get_option('systemd_user_unit_dir')
if servicedir == ''
  servicedir = systemd_dep.get_pkgconfig_variable('systemduserunitdir')
endif

if servicedir == ''
  error('Couldn\'t determine systemd user unit service directory')
endif

conf_data = configuration_data()
conf_data.set('version', meson.project_version())
configure_file(input: 'gnome-ponytail-daemon.spec.in',
               output: 'gnome-ponytail-daemon.spec',
               configuration: conf_data)

subdir('src')
if get_option('ponytail_python')
  subdir('ponytail')
endif

