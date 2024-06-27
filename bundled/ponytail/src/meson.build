send_event = files([
  'gnome-ponytail-daemon.c',
  'gpd-context.c',
  'gpd-context.h',
  'gpd-session.c',
  'gpd-session.h',
  'gpd-event-controller.c',
  'gpd-event-controller.h',
  'gpd-keyboard-utils.c',
  'gpd-keyboard-utils.h',
  'gpd-stream.c',
  'gpd-stream.h',
  'gpd.h'])

if libei_dep.found()
  send_event += [
    'gpd-ei-client.c',
    'gpd-ei-client.h',
  ]
endif

gen_sources = []

gen_sources += gnome.gdbus_codegen('gpd-dbus-screen-cast',
                                   'org.gnome.Mutter.ScreenCast.xml',
                                   interface_prefix: 'org.gnome.Mutter.',
                                   namespace: 'GpdDBus')

gen_sources += gnome.gdbus_codegen('gpd-dbus-remote-desktop',
                                   'org.gnome.Mutter.RemoteDesktop.xml',
                                   interface_prefix: 'org.gnome.Mutter.',
                                   namespace: 'GpdDBus')

gen_sources += gnome.gdbus_codegen('gpd-dbus-event-controller',
                                   'org.gnome.Ponytail.EventController.xml',
                                   interface_prefix: 'org.gnome.Ponytail.',
                                   namespace: 'GpdDBus')

send_event += gen_sources

prefix = get_option('prefix')
libexecdir = join_paths(prefix, get_option('libexecdir'))

config_h = configuration_data()
config_h.set10('GPD_HAS_LIBEI', libei_dep.found())
configure_file(input : 'config.h.in',
               output : 'config.h',
               configuration : config_h)
config_h_dir = include_directories('.')

executable('gnome-ponytail-daemon',
           send_event,
           dependencies: [glib_dep,
                          gio_dep,
                          gio_unix_dep,
                          libei_dep,
                          libxkbcommon_dep],
           include_directories: [config_h_dir],
           install : true,
           install_dir: libexecdir)

service_config = configuration_data()
service_config.set('libexecdir', libexecdir)

configure_file(input: 'gnome-ponytail-daemon.service.in',
               output: 'gnome-ponytail-daemon.service',
               configuration: service_config,
               install_dir: servicedir)

configure_file(input: 'org.gnome.Ponytail.service.in',
               output: 'org.gnome.Ponytail.service',
               configuration: service_config,
               install_dir: dbusservicedir)
