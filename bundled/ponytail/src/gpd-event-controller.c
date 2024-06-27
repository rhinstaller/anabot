/*
 * Copyright (C) 2018 Red Hat Inc.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * gnome-ponytail-daemon for dogtail written by:
 *   Olivier Fourdan <ofourdan@redhat.com>
 * 
 * Based on gnome-remote-desktop written by:
 *   Jonas Ådahl <jadahl@gmail.com>
 */
	
#include <linux/input.h>

#include "gpd-session.h"
#include "gpd-event-controller.h"
#include "gpd-keyboard-utils.h"
#include "gpd.h"

struct _GpdEventController
{
  GpdSession parent;
  GpdDBusEventController *proxy;
};

G_DEFINE_TYPE (GpdEventController, gpd_event_controller, GPD_TYPE_SESSION);

static uint32_t
translate_button_to_code (int button)
{
  uint32_t button_code;

  g_debug ("%s", __func__);
  switch (button)
    {
    case 1:
      button_code = BTN_LEFT;
      break;
    case 2:
      button_code = BTN_MIDDLE;
      break;
    case 3:
      button_code = BTN_RIGHT;
      break;
    case 8:
      button_code = BTN_SIDE;
      break;
    case 9:
      button_code = BTN_EXTRA;
      break;
    default:
      g_warning ("Unsupported button number %i", button);
      button_code = 0;
    }

  return button_code;
}

static gboolean
on_connect_window (GpdDBusEventController *proxy,
                   GDBusMethodInvocation  *invocation,
                   uint64_t                window_id,
                   GpdEventController     *event_controller)
{
  gboolean success;

  g_debug ("%s", __func__);
  success = gpd_session_connect_window (GPD_SESSION (event_controller), window_id);
  if (!success)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Failed to connect to window");
      return TRUE;
    }
  gpd_dbus_event_controller_complete_connect_window (proxy, invocation);

  return TRUE;
}

static gboolean
on_connect_monitor (GpdDBusEventController *proxy,
                    GDBusMethodInvocation  *invocation,
                    const char             *connector,
                    GpdEventController     *event_controller)
{
  gboolean success;

  g_debug ("%s", __func__);
  success = gpd_session_connect_monitor (GPD_SESSION (event_controller), connector);
  if (!success)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Failed to connect to monitor");
      return TRUE;
    }
  gpd_dbus_event_controller_complete_connect_monitor (proxy, invocation);

  return TRUE;
}

static gboolean
on_disconnect (GpdDBusEventController *proxy,
               GDBusMethodInvocation  *invocation,
               GpdEventController     *event_controller)
{
  g_debug ("%s", __func__);
  gpd_session_restart (GPD_SESSION (event_controller));
  gpd_dbus_event_controller_complete_disconnect (proxy, invocation);

  return TRUE;
}

static gboolean
on_generate_keycode_event (GpdDBusEventController *proxy,
                          GDBusMethodInvocation  *invocation,
                          unsigned int            keycode,
                          gboolean                pressed,
                          GpdEventController     *event_controller)
{
  gboolean success;

  g_debug ("%s", __func__);
  if (keycode < 8)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Keycode invalid");
      return TRUE;
    }
  success = gpd_session_notify_keyboard_keycode (GPD_SESSION (event_controller),
                                                 xkb_keycode_to_evdev (keycode),
                                                 pressed);
  if (!success)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Failed to generate keycode event");
      return TRUE;
    }
  gpd_dbus_event_controller_complete_generate_keycode_event (proxy, invocation);

  return TRUE;
}

static gboolean
on_generate_keysym_event (GpdDBusEventController *proxy,
                          GDBusMethodInvocation  *invocation,
                          unsigned int            keysym,
                          gboolean                pressed,
                          GpdEventController     *event_controller)
{
  gboolean success;

  g_debug ("%s", __func__);
  success = gpd_session_notify_keyboard_keysym (GPD_SESSION (event_controller),
                                                keysym,
                                                pressed);
  if (!success)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Failed to generate keysym event");
      return TRUE;
    }
  gpd_dbus_event_controller_complete_generate_keysym_event (proxy, invocation);

  return TRUE;
}

static gboolean
on_generate_button_event (GpdDBusEventController *proxy,
                          GDBusMethodInvocation  *invocation,
                          int                     button,
                          gboolean                pressed,
                          GpdEventController     *event_controller)
{
  uint32_t button_code = translate_button_to_code (button);
  gboolean success;

  g_debug ("%s", __func__);
  if (button_code == 0)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Unsupported button");
      return TRUE;
    }
  success = gpd_session_notify_pointer_button (GPD_SESSION (event_controller),
                                               button_code,
                                               pressed);
  if (!success)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Failed to send button event");
      return TRUE;
    }
  gpd_dbus_event_controller_complete_generate_button_event (proxy, invocation);

  return TRUE;
}

static gboolean
on_generate_motion_event (GpdDBusEventController *proxy,
                          GDBusMethodInvocation  *invocation,
                          double                  x,
                          double                  y,
                          GpdEventController     *event_controller)
{
  gboolean success;

  g_debug ("%s", __func__);
  success = gpd_session_notify_pointer_motion_absolute (GPD_SESSION (event_controller),
                                                        x, y);
  if (!success)
    {
      g_dbus_method_invocation_return_error (invocation, G_DBUS_ERROR,
                                             G_DBUS_ERROR_FAILED,
                                             "Failed to generate motion event");
      return TRUE;
    }
  gpd_dbus_event_controller_complete_generate_motion_event (proxy, invocation);

  return TRUE;
}

static void
on_name_acquired (GDBusConnection *connection,
                  const gchar     *name,
                  gpointer         data)
{
  g_debug ("%s", __func__);
}

static void
on_name_lost (GDBusConnection *connection,
              const gchar     *name,
              gpointer         data)
{
  g_debug ("%s", __func__);
  g_application_release (g_application_get_default ());
}

static gboolean
init_event_controller (GpdEventController *event_controller)
{
  GDBusConnection *connection;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);

  g_signal_handlers_disconnect_by_func (event_controller,
                                        G_CALLBACK (init_event_controller),
                                        NULL);

  connection = g_bus_get_sync (G_BUS_TYPE_SESSION, NULL, &error);

  if (error != NULL)
    {
      g_critical ("error getting session bus: %s", error->message);
      return FALSE;
    }

  event_controller->proxy = gpd_dbus_event_controller_skeleton_new ();
  g_dbus_interface_skeleton_export (G_DBUS_INTERFACE_SKELETON (event_controller->proxy),
                                    connection,
                                    "/org/gnome/Ponytail/EventController",
                                    &error);

  if (error != NULL)
    {
      g_critical ("error exporting manager on session bus: %s", error->message);
      return FALSE;
    }

  g_bus_own_name_on_connection (connection,
                                "org.gnome.Ponytail",
                                G_BUS_NAME_OWNER_FLAGS_NONE,
                                on_name_acquired,
                                on_name_lost,
                                NULL,
                                NULL);

  g_signal_connect (event_controller->proxy,
                    "handle-connect-window",
                    G_CALLBACK (on_connect_window),
                    event_controller);

  g_signal_connect (event_controller->proxy,
                    "handle-connect-monitor",
                    G_CALLBACK (on_connect_monitor),
                    event_controller);

  g_signal_connect (event_controller->proxy,
                    "handle-disconnect",
                    G_CALLBACK (on_disconnect),
                    event_controller);

  g_signal_connect (event_controller->proxy,
                    "handle-generate-keycode-event",
                    G_CALLBACK (on_generate_keycode_event),
                    event_controller);

  g_signal_connect (event_controller->proxy,
                    "handle-generate-keysym-event",
                    G_CALLBACK (on_generate_keysym_event),
                    event_controller);

  g_signal_connect (event_controller->proxy,
                    "handle-generate-button-event",
                    G_CALLBACK (on_generate_button_event),
                    event_controller);

  g_signal_connect (event_controller->proxy,
                    "handle-generate-motion-event",
                    G_CALLBACK (on_generate_motion_event),
                    event_controller);

  return TRUE;
}

GpdEventController *
gpd_event_controller_new (GpdContext *context)
{
  GpdEventController *event_controller;

  g_debug ("%s", __func__);
  event_controller = g_object_new (GPD_TYPE_EVENT_CONTROLLER,
                                   "context", context,
                                   NULL);
  g_signal_connect (event_controller,
                    "acquired",
                    G_CALLBACK (init_event_controller),
                    NULL);

  return event_controller;
}

static void
gpd_event_controller_stop (GpdSession *session)
{
  GpdEventController *event_controller = GPD_EVENT_CONTROLLER (session);

  g_debug ("%s", __func__);
  gpd_dbus_event_controller_emit_disconnected (event_controller->proxy);
}

static void
gpd_event_controller_stream_ready (GpdSession *session,
                                   GpdStream  *stream)
{
  GpdEventController *event_controller = GPD_EVENT_CONTROLLER (session);

  g_debug ("%s", __func__);
  gpd_dbus_event_controller_emit_connected (event_controller->proxy);
}

static void
gpd_event_controller_init (GpdEventController *event_controller)
{
  g_debug ("%s", __func__);
}

static void
gpd_event_controller_class_init (GpdEventControllerClass *klass)
{
  GpdSessionClass *session_class = GPD_SESSION_CLASS (klass);

  g_debug ("%s", __func__);
  session_class->stop = gpd_event_controller_stop;
  session_class->stream_ready = gpd_event_controller_stream_ready;
}
