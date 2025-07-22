#
# Copyright (C) 2018 Red Hat Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#   Olivier Fourdan <ofourdan@redhat.com>
#

import dbus
import atexit
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
from time import sleep

class Ponytail:

    """
    Implements the D-BUS interactions with gnome-ponytail-daemon interfaces.
    """
    def __init__(self):
        self.main_loop = GLib.MainLoop()
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.ponytail_iface = 'org.gnome.Ponytail'
        self.event_controller_iface = 'org.gnome.Ponytail.EventController'
        self.shell_introspect_iface = 'org.gnome.Shell.Introspect'
        self.event_controller = self.bus.get_object(self.ponytail_iface,
                                                    '/org/gnome/Ponytail/EventController')
        self.shell_introspect = self.bus.get_object(self.shell_introspect_iface,
                                                    '/org/gnome/Shell/Introspect')
        self.connected = None

        atexit.register(self.disconnect)

    def __call__(self):
        return self

    def _windowMatch(self, params, name, want_focus):
        # If we expect the window to be focused while it's not, ignore
        if (want_focus and not params['has-focus']):
            return False
        # First, try the "app-id"
        if (params["app-id"] == name):
            return True
        # Second, try the window title
        if ("title" in params and params["title"] == name):
            return True
        # Last, try the wm-class without case
        if ("wm-class" in params and params["wm-class"].lower() == name.lower()):
            return True
        return False

    def getWindows(self):
        return self.shell_introspect.GetWindows(dbus_interface=self.shell_introspect_iface)

    @property
    def window_list(self):
        windows = self.getWindows()
        window_list = []
        for window in windows.keys():
            (window_id, params) = (window, windows[window])
            params = dict(params)
            params['id'] = int(window_id)
            window_list.append(params)
        return window_list

    def getWindowId(self, name, want_focus=False):
        window_list = self.getWindows()
        for window in window_list.keys():
            (window_id, params) = (window, window_list[window])
            params = dict(params)
            if (self._windowMatch(params, name, want_focus)):
                return window_id
        # Otherwise raise an error
        raise ValueError('Window not found')

    def waitFor(self, name, timeout=30, delay=.5):
        waitloop = GLib.MainLoop()
        windowid = None
        tag = None

        def appChanged():
            try:
                temp_id = self.getWindowId(name, True)
            except:
                temp_id = None

            if (temp_id):
                nonlocal windowid
                nonlocal tag
                GLib.source_remove(tag)
                windowid = temp_id
                sleep(delay)
                waitloop.quit()

        def onTimeout():
            waitloop.quit()

        self.bus.add_signal_receiver(appChanged, 'RunningApplicationsChanged',
                                     self.shell_introspect_iface)

        # First check if the window is already mapped and focused
        try:
            windowid = self.getWindowId(name, True)
        except:
            pass

        if (windowid):
            self.bus.remove_signal_receiver(appChanged,
                                            'RunningApplicationsChanged',
                                            self.shell_introspect_iface)
            return windowid;

        # Otherwise, Use the introspection API to wait for the window
        # to show up and be focused
        tag = GLib.timeout_add_seconds(timeout, onTimeout)
        waitloop.run()
        self.bus.remove_signal_receiver(appChanged, 'RunningApplicationsChanged',
                                        self.shell_introspect_iface)
        if (windowid is not None):
            return windowid

        raise ValueError('Timeout waiting for Window')

    def generateKeycodePress(self, keycode):
        self.event_controller.GenerateKeycodeEvent(dbus.Int32(keycode),
                                                   dbus.Boolean(1),
                                                   dbus_interface=self.event_controller_iface)

    def generateKeycodeRelease(self, keycode):
        self.event_controller.GenerateKeycodeEvent(dbus.Int32(keycode),
                                                   dbus.Boolean(0),
                                                   dbus_interface=self.event_controller_iface)

    def generateKeycodeEvent(self, keycode, delay=.05):
        self.generateKeycodePress(keycode)
        sleep(delay)
        self.generateKeycodeRelease(keycode)
        sleep(delay)

    def generateKeysymPress(self, keysym):
        self.event_controller.GenerateKeysymEvent(dbus.Int32(keysym),
                                              dbus.Boolean(1),
                                              dbus_interface=self.event_controller_iface)

    def generateKeysymRelease(self, keysym):
        self.event_controller.GenerateKeysymEvent(dbus.Int32(keysym),
                                              dbus.Boolean(0),
                                              dbus_interface=self.event_controller_iface)

    def generateKeysymEvent(self, keysym, delay=.05):
        self.generateKeysymPress(keysym)
        sleep(delay)
        self.generateKeysymRelease(keysym)
        sleep(delay)

    def generateButtonPress(self, button):
        self.event_controller.GenerateButtonEvent(dbus.Int32(button),
                                              dbus.Boolean(1),
                                              dbus_interface=self.event_controller_iface)

    def generateButtonRelease(self, button):
        self.event_controller.GenerateButtonEvent(dbus.Int32(button),
                                              dbus.Boolean(0),
                                              dbus_interface=self.event_controller_iface)

    def generateMotionEvent(self, x, y):
        self.event_controller.GenerateMotionEvent(dbus.Double(x),
                                              dbus.Double(y),
                                              dbus_interface=self.event_controller_iface)

    def generateButtonEvent(self, button, x=None, y=None, delay=.05):
        if x is not None and y is not None:
            self.generateMotionEvent(x, y)
        self.generateButtonPress(button)
        sleep(delay)
        self.generateButtonRelease(button)
        sleep(delay)

    def connectWindow(self, windowid):
        waitloop = GLib.MainLoop()

        def connected():
            waitloop.quit()

        self.bus.add_signal_receiver(connected, 'Connected', self.event_controller_iface)
        self.event_controller.ConnectWindow(windowid, dbus_interface=self.event_controller_iface)
        waitloop.run()
        self.bus.remove_signal_receiver(connected, 'Connected', self.event_controller_iface)
        self.connected = windowid

    def connectMonitor(self, monitor=""):
        waitloop = GLib.MainLoop()

        def connected():
            waitloop.quit()

        self.bus.add_signal_receiver(connected, 'Connected', self.event_controller_iface)
        self.event_controller.ConnectMonitor(monitor, dbus_interface=self.event_controller_iface)
        waitloop.run()
        self.bus.remove_signal_receiver(connected, 'Connected', self.event_controller_iface)
        self.connected = monitor

    def disconnect(self, force=False):
        if self.connected is None and not force:
            return

        waitloop = GLib.MainLoop()

        def disconnected():
            waitloop.quit()

        self.bus.add_signal_receiver(disconnected, 'Disconnected', self.event_controller_iface)
        self.event_controller.Disconnect(dbus_interface=self.event_controller_iface)
        if not force:
            waitloop.run()
        self.bus.remove_signal_receiver(disconnected, 'Disconnected', self.event_controller_iface)
        self.connected = None
