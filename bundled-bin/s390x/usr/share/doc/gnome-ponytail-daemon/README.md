gnome-ponytail-daemon
=====================

gnome-ponytail-daemon is a helper daemon intended for dogtail on Wayland.

On X11, dogtail relies on XTest extension to generate pointer and keyboard
events, but there is no equivalent on Wayland.

On GNOME on Wayland, however, there are the screen-cast and remote-desktop APIs
that can be used for controlling the keyboard and pointer.

Also, Wayland does not expose global coordinates, and ATK will return local
coordinates of the various application widgets on Wayland, this is where the
RecordWindow method from screencast can be used, as it will translate global
coordinates into surface relative coordinates.

Obviously, to be able to record or a given window, one needs a way to identify
such a window, this is where the window-list API comes in.

The Introspect D-BUS API in mutter provides a way to list all toplevel windows.

Dependencies
------------

gnome-ponytail-daemon relies on [glib](https://developer.gnome.org/glib/)

Building
--------

gnome-ponytail-daemon uses the [Meson build system](https://mesonbuild.com/),
building is just a matter of running within the source directory:

```
$ meson setup build
$ ninja -C build
```

Usage
-----

gnome-ponytail-daemon uses GLIB, for debugging purpose it's possible to increase
the loglevel using G_MESSAGES_DEBUG:

```
$ G_MESSAGES_DEBUG=all ./build/src/gnome-ponytail-daemon
** (process:2082): DEBUG: 09:48:03.916: main
** (process:2082): DEBUG: 09:48:03.916: gpd_app_class_init
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.919: gpd_app_startup
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.919: on_remote_desktop_name_appeared
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.920: on_screen_cast_name_appeared
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.922: on_remote_desktop_proxy_acquired
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: on_screen_cast_proxy_acquired
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_event_controller_new
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_session_class_init
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_event_controller_class_init
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_session_init
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_event_controller_init
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_session_set_property
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: init_event_controller
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.923: gpd_session_start
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.924: on_remote_desktop_session_created
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.927: on_remote_desktop_session_proxy_acquired
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.927: on_screen_cast_session_created
** (gnome-ponytail-daemon:2082): DEBUG: 09:48:03.930: on_screen_cast_session_proxy_acquired
```

Testing
-------

1. Make sure to use a version of mutter which support the “RecordWindow”
implementation
2. Make sure to use a version of gnome-shell with support for the “Introspect” D-BUS API
3. Enable Introspect support:
- With GNOME Shell 41 and above:<br/>
  Enable Introspect support in Looking Glass. Press `Alt+F2`, type `lg` and
  press enter to open Looking Glass. Finally enable unsafe mode:
  ```
  >>> global.context.unsafe_mode = true
  ```
- With GNOME Shell up to GNOME 40:<br/>
  Enable Introspect support by setting **introspect** to **true** in
  org.gnome.shell settings:
  ```
  $ gsettings set org.gnome.shell introspect true
  ```
3. Get the list of windows
```
$ dbus-send --session --print-reply --dest=org.gnome.Shell.Introspect /org/gnome/Shell/Introspect org.gnome.Shell.Introspect.GetWindows
   array [
      dict entry(
         uint64 4272836639
         array [
            dict entry(
               string "title"
               variant                   string "Calculator"
            )
            dict entry(
               string "class"
               variant                   string "gnome-calculator"
            )
            dict entry(
               string "type"
               variant                   uint32 0
            )
            dict entry(
               string "is_visible"
               variant                   boolean true
            )
            dict entry(
               string "has_focus"
               variant                   boolean false
            )
            dict entry(
               string "width"
               variant                   int32 356
            )
            dict entry(
               string "height"
               variant                   int32 418
            )
            dict entry(
               string "pid"
               variant                   uint64 31396
            )
         ]
      )
   ]
```
4. Connect to a window, e.g. gnome-calculator, using its `window-id`
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.ConnectWindow uint64:4272836639
```
_The orange "remote-session" icon should show up in gnome-shell at this point._

5. Generate some motion event
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.GenerateMotionEvent double:30 double:270
```
_This will move the pointer within the gnome-calculator at the given relative location._

6. Generate mouse button events
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.GenerateButtonEvent int32:1 boolean:true

$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.GenerateButtonEvent int32:1 boolean:false
```
**Make sure to send a release event for each press event!**

7. Generate keycode events events
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.GenerateKeycodeEvent uint32:90 boolean:true

$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.GenerateKeycodeEvent uint32:90 boolean:false
```
**Make sure to send a release event for each press event!**

_Note: The keycode used are the same as reported by "xev" on X11, i.e. XKB keycodes, not evdev keycodes._

8. Disconnect from the window
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.Disconnect
```
_The orange "remote-session" icon should disappear in gnome-shell._

9. Connect to the primary monitor
```
$  dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.ConnectMonitor string:""
```
_The orange "remote-session" icon should show up again in gnome-shell._

10. Generate some motion event
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.GenerateMotionEvent double:100 double:100
```
_This will move the pointer at the given global location_

11. Disconnect from the monitor
```
$ dbus-send --session --print-reply --dest=org.gnome.Ponytail /org/gnome/Ponytail/EventController org.gnome.Ponytail.EventController.Disconnect
```
_The orange "remote-session" icon should disappear in gnome-shell._

The "Ponytail" Python module
----------------------------

gnome-ponytail-daemon comes with a Python module called ["Ponytail"](ponytail/ponytail.py)
aimed at simplifying the connect/disconnect phases (which need to wait for a signal for
completion) and hide the possible future API change behind a more stable API.

A complete example is provided in [examples/test-ponytail.py](examples/test-ponytail.py)

1. Initiating the module

```python
#!/usr/bin/python3

from ponytail.ponytail import Ponytail

try:
    ponytail = Ponytail()
except Exception:
    print ("Fail to initialize Ponytail interfaces")
    exit()
```

2. Getting the window-id of an existing window

```python
try:
    windowid = ponytail.getWindowId("org.gnome.Calculator.desktop")
except ValueError:
    print("No gnome-calculator found")
    exit()
```
3. Or waiting for a client window to appear after it was launched

```python
subprocess.Popen(["gnome-calculator", "-m", "basic"])
try:
    windowid = ponytail.waitFor("org.gnome.Calculator.desktop", timeout=3)
except ValueError:
    print("No gnome-calculator found")
    exit()
```

4. Connecting to the window through gnome-ponytail-daemon
```python
ponytail.connectWindow(windowid)
```

5. Disconnecting
```python
ponytail.disconnect()
```

Credits
-------

gnome-ponytail-daemon for dogtail written by @ofourdan based on
[gnome-remote-desktop](https://gitlab.gnome.org/jadahl/gnome-remote-desktop)
written by @jadahl.
