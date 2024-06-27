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

#include <glib.h>
#include <libei.h>

#include "gpd-ei-client.h"
#include "gpd-keyboard-utils.h"

#define EI_CONNECTION_TIMEOUT 5000

struct _GpdEiClient
{
  GObject parent;

  GpdDBusRemoteDesktopSession *session_proxy;
  GCancellable *cancellable;
  GIOChannel *io_channel;
  guint io_channel_source;
  struct ei *ei;
  gboolean ei_connected;
  guint connection_timer;
  struct ei_seat *ei_seat;
  uint32_t ei_sequence;
  gboolean has_pointer;
  struct ei_device *pointer;
  gboolean has_keyboard;
  struct ei_device *keyboard;
  struct xkb_context *xkb_context;
  struct xkb_keymap *xkb_keymap;
  struct xkb_state *xkb_state;
};

G_DEFINE_TYPE (GpdEiClient, gpd_ei_client, G_TYPE_OBJECT);

enum
{
  SIGNAL_CONNECTED,
  SIGNAL_DISCONNECTED,
  SIGNAL_ERROR,

  N_SIGNALS,
};

static guint signals[N_SIGNALS];

/* SupportedDeviceTypes as defined in org.gnome.Mutter.RemoteDesktop.xml */
enum
{
  DEVICE_TYPE_KEYBOARD = 1,
  DEVICE_TYPE_POINTER = 2,
  DEVICE_TYPE_TOUCHSCREEN = 4,
};

static void
gpd_ei_client_init (GpdEiClient *event_controller)
{
  g_debug ("%s", __func__);
}

static void
gpd_ei_client_finalize (GObject *object)
{
  GpdEiClient *ei_client = GPD_EI_CLIENT (object);

  g_debug ("%s", __func__);

  if (ei_client->cancellable)
    g_cancellable_cancel (ei_client->cancellable);
  g_clear_object (&ei_client->cancellable);

  g_clear_handle_id (&ei_client->connection_timer, g_source_remove);

  if (ei_client->io_channel)
    {
      g_io_channel_shutdown (ei_client->io_channel, FALSE, NULL);
      g_source_remove (ei_client->io_channel_source);
      ei_client->io_channel_source = 0;
      g_io_channel_unref (ei_client->io_channel);
    }

  xkb_context_unref (ei_client->xkb_context);
  xkb_keymap_unref (ei_client->xkb_keymap);
  xkb_state_unref (ei_client->xkb_state);

  if (ei_client->has_pointer)
    ei_device_unref (ei_client->pointer);

  if (ei_client->has_keyboard)
    ei_device_unref (ei_client->keyboard);

  if (ei_client->ei)
    ei_unref (ei_client->ei);

  G_OBJECT_CLASS (gpd_ei_client_parent_class)->finalize (object);
}

static void
gpd_ei_client_class_init (GpdEiClientClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);

  g_debug ("%s", __func__);

  object_class->finalize = gpd_ei_client_finalize;

  signals[SIGNAL_CONNECTED] = g_signal_new ("connected",
                                            G_TYPE_FROM_CLASS (klass),
                                            G_SIGNAL_RUN_LAST,
                                            0,
                                            NULL, NULL, NULL,
                                            G_TYPE_NONE, 0);
  signals[SIGNAL_DISCONNECTED] = g_signal_new ("disconnected",
                                               G_TYPE_FROM_CLASS (klass),
                                               G_SIGNAL_RUN_LAST,
                                               0,
                                               NULL, NULL, NULL,
                                               G_TYPE_NONE, 0);
  signals[SIGNAL_ERROR] = g_signal_new ("error",
                                        G_TYPE_FROM_CLASS (klass),
                                        G_SIGNAL_RUN_LAST,
                                        0,
                                        NULL, NULL, NULL,
                                        G_TYPE_NONE, 0);
}

GpdEiClient *
gpd_ei_client_new (GpdDBusRemoteDesktopSession *session_proxy)
{
  GpdEiClient *ei_client;

  g_debug ("%s", __func__);
  ei_client = g_object_new (GPD_TYPE_EI_CLIENT, NULL);
  ei_client->session_proxy = session_proxy;

  return ei_client;
}

static gboolean
on_ei_connection_timeout (gpointer user_data)
{
  GpdEiClient *ei_client = user_data;

  g_debug ("%s: connected? %s",
           __func__,
           ei_client->ei_connected ? "Yes" : "No");

  if (!ei_client->ei_connected)
    g_signal_emit (ei_client, signals[SIGNAL_ERROR], 0);

  return G_SOURCE_REMOVE;
}

static void
on_ei_event_connect (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  g_debug ("%s", __func__);

  /* We emit the connected signal once the connection to EIS is established and
   * the required input devices are available. If this timer expires before all
   * required input devices are available, we emit the error signal. */
  ei_client->connection_timer = g_timeout_add (EI_CONNECTION_TIMEOUT,
                                               on_ei_connection_timeout,
                                               ei_client);
}

static void
on_ei_event_disconnect (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  g_debug ("%s", __func__);
  ei_client->ei_connected = FALSE;
  g_signal_emit (ei_client, signals[SIGNAL_DISCONNECTED], 0);
}

static void
on_ei_event_seat_added (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  g_debug ("%s", __func__);

  if (ei_client->ei_seat)
    return;

  ei_client->ei_seat = ei_seat_ref (ei_event_get_seat (ei_event));
  ei_seat_bind_capabilities (ei_client->ei_seat,
                             EI_DEVICE_CAP_POINTER,
                             EI_DEVICE_CAP_POINTER_ABSOLUTE,
                             EI_DEVICE_CAP_KEYBOARD,
                             EI_DEVICE_CAP_TOUCH,
                             EI_DEVICE_CAP_BUTTON,
                             EI_DEVICE_CAP_SCROLL,
                             NULL);
}

static void
on_ei_event_seat_removed (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  g_debug ("%s", __func__);

  if (ei_event_get_seat (ei_event) == ei_client->ei_seat)
    ei_client->ei_seat = ei_seat_unref(ei_client->ei_seat);
}

static void
on_ei_event_device_added (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  struct ei_device *ei_device = ei_event_get_device (ei_event);
  g_debug ("%s", __func__);

  if (!ei_client->pointer &&
      ei_device_has_capability (ei_device, EI_DEVICE_CAP_POINTER_ABSOLUTE) &&
      ei_device_has_capability (ei_device, EI_DEVICE_CAP_BUTTON) &&
      ei_device_has_capability (ei_device, EI_DEVICE_CAP_SCROLL))
    {
      g_debug ("%s pointer", __func__);
      ei_client->pointer = ei_device_ref (ei_device);
    }
  else if (!ei_client->keyboard &&
           ei_device_has_capability (ei_device, EI_DEVICE_CAP_KEYBOARD))
    {
      g_debug ("%s keyboard", __func__);
      g_autoptr (GError) error = NULL;

      if (!process_ei_keyboard (ei_device,
                                &ei_client->xkb_context,
                                &ei_client->xkb_keymap,
                                &ei_client->xkb_state,
                                &error))
        {
          g_warning ("Failed to process EI keyboard: %s", error->message);
          return;
        }

      ei_client->keyboard = ei_device_ref (ei_device);
    }
}

static void
on_ei_event_device_resumed (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  struct ei_device *ei_device = ei_event_get_device (ei_event);
  g_debug ("%s", __func__);

  if (ei_device == ei_client->pointer)
    {
      g_debug ("%s pointer", __func__);
      ei_device_start_emulating (ei_client->pointer, ++ei_client->ei_sequence);
      ei_client->has_pointer = TRUE;
    }
  else if (ei_device == ei_client->keyboard)
    {
      g_debug ("%s keyboard", __func__);
      ei_device_start_emulating (ei_client->keyboard, ++ei_client->ei_sequence);
      ei_client->has_keyboard = TRUE;
    }

  if (!ei_client->ei_connected &&
      ei_client->has_pointer &&
      ei_client->has_keyboard)
    {
      g_debug ("%s all devices found, connected", __func__);

      g_source_remove (ei_client->connection_timer);
      ei_client->connection_timer = 0;

      ei_client->ei_connected = TRUE;
      g_signal_emit (ei_client, signals[SIGNAL_CONNECTED], 0);
    }
}

static void
on_ei_event_device_paused (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  struct ei_device *ei_device = ei_event_get_device (ei_event);
  g_debug ("%s", __func__);

  if (ei_device == ei_client->pointer)
    {
      g_debug ("%s pointer", __func__);
      ei_client->has_pointer = FALSE;
    }
  else if (ei_device == ei_client->keyboard)
    {
      g_debug ("%s keyboard", __func__);
      ei_client->has_keyboard = FALSE;
    }
}

static void
on_ei_event_device_removed (GpdEiClient *ei_client, struct ei_event *ei_event)
{
  struct ei_device *ei_device = ei_event_get_device (ei_event);
  g_debug ("%s", __func__);

  if (ei_device == ei_client->pointer)
    {
      g_debug ("%s pointer", __func__);
      ei_device_unref (ei_client->pointer);
      ei_client->has_pointer = FALSE;
    }
  else if (ei_device == ei_client->keyboard)
    {
      g_debug ("%s keyboard", __func__);
      ei_device_unref (ei_client->keyboard);
      ei_client->has_keyboard = FALSE;
    }
}

static gboolean
on_ei_event (GIOChannel   *source,
			       GIOCondition  condition,
			       gpointer      data)
{
  GpdEiClient *ei_client = data;

  g_debug ("%s", __func__);
  ei_dispatch (ei_client->ei);

  while (TRUE)
    {
      struct ei_event *ei_event = ei_get_event (ei_client->ei);
      if (!ei_event)
        break;

      switch (ei_event_get_type (ei_event))
        {
          case EI_EVENT_CONNECT:
            on_ei_event_connect (ei_client, ei_event);
            break;
          case EI_EVENT_DISCONNECT:
            on_ei_event_disconnect (ei_client, ei_event);
            break;
          case EI_EVENT_SEAT_ADDED:
            on_ei_event_seat_added (ei_client, ei_event);
            break;
          case EI_EVENT_SEAT_REMOVED:
            on_ei_event_seat_removed (ei_client, ei_event);
            break;
          case EI_EVENT_DEVICE_ADDED:
            on_ei_event_device_added (ei_client, ei_event);
            break;
          case EI_EVENT_DEVICE_RESUMED:
            on_ei_event_device_resumed (ei_client, ei_event);
            break;
          case EI_EVENT_DEVICE_PAUSED:
            on_ei_event_device_paused (ei_client, ei_event);
            break;
          case EI_EVENT_DEVICE_REMOVED:
            on_ei_event_device_removed (ei_client, ei_event);
            break;
          default:
            break;
        }

      ei_event_unref (ei_event);
    }

  return G_SOURCE_CONTINUE;
}

static gboolean
init_ei (GpdEiClient *ei_client, int fd)
{
  g_debug ("%s", __func__);

  ei_client->ei = ei_new_sender (ei_client);
  if (ei_setup_backend_fd (ei_client->ei, fd) != 0)
    return FALSE;

  ei_client->io_channel = g_io_channel_unix_new (ei_get_fd (ei_client->ei));
  g_io_channel_set_encoding (ei_client->io_channel, NULL, NULL);
  ei_client->io_channel_source = g_io_add_watch (ei_client->io_channel,
                                                 G_IO_IN,
                                                 on_ei_event,
                                                 ei_client);
  return TRUE;
}

static void
on_connect_to_eis_finished (GObject      *object,
                            GAsyncResult *result,
                            gpointer      user_data)
{
  GpdEiClient *ei_client = user_data;
  g_autoptr (GVariant) fd_variant = NULL;
  g_autoptr (GUnixFDList) fd_list = NULL;
  g_autoptr (GError) error = NULL;
  int fd = -1;

  g_debug ("%s", __func__);

  if (!gpd_dbus_remote_desktop_session_call_connect_to_eis_finish (ei_client->session_proxy,
                                                                   &fd_variant,
                                                                   &fd_list,
                                                                   result,
                                                                   &error))
    {
      g_warning ("Failed to connect to EIS: %s", error->message);
      g_signal_emit (ei_client, signals[SIGNAL_ERROR], 0);
      return;
    }

  fd = g_unix_fd_list_get (fd_list, g_variant_get_handle (fd_variant), &error);
  if (fd < 0)
    {
      g_warning ("Failed to get EIS file descriptor: %s", error->message);
      g_signal_emit (ei_client, signals[SIGNAL_ERROR], 0);
      return;
    }

  if (!init_ei (ei_client, fd))
    {
      g_warning ("Error initializing EI");
      g_signal_emit (ei_client, signals[SIGNAL_ERROR], 0);
      return;
    }
}

void
gpd_ei_client_start (GpdEiClient *ei_client)
{
  GVariantBuilder connect_args_builder;
  GVariant *connect_args;
  guint device_types = DEVICE_TYPE_KEYBOARD | DEVICE_TYPE_POINTER;

  g_debug ("%s", __func__);

  ei_client->cancellable = g_cancellable_new ();

  g_variant_builder_init (&connect_args_builder, G_VARIANT_TYPE ("a{sv}"));
  g_variant_builder_add (&connect_args_builder,
                         "{sv}",
                         "device-types",
                         g_variant_new_uint32 (device_types));
  connect_args = g_variant_builder_end (&connect_args_builder);

  gpd_dbus_remote_desktop_session_call_connect_to_eis (ei_client->session_proxy,
                                                       connect_args,
                                                       NULL,
                                                       ei_client->cancellable,
                                                       on_connect_to_eis_finished,
                                                       ei_client);
}

gboolean
gpd_ei_client_is_connected (GpdEiClient *ei_client)
{
  return ei_client->ei_connected;
}

gboolean
gpd_ei_client_has_keyboard (GpdEiClient *ei_client)
{
  return ei_client->has_keyboard;
}

gboolean
gpd_ei_client_has_pointer (GpdEiClient *ei_client)
{
  return ei_client->has_pointer;
}

gboolean
gpd_ei_client_notify_keyboard_keycode (GpdEiClient *ei_client,
                                       guint        keycode,
                                       gboolean     is_press)
{
  g_debug ("%s", __func__);

  if (!ei_client->ei_connected || !ei_client->has_keyboard)
    {
      g_warning ("EI keyboard device not available");
      return FALSE;
    }

  ei_device_keyboard_key (ei_client->keyboard, keycode, is_press);
  ei_device_frame (ei_client->keyboard, ei_now (ei_client->ei));

  return TRUE;
}

gboolean
gpd_ei_client_notify_keyboard_keysym (GpdEiClient *ei_client,
                                      guint        keysym,
                                      gboolean     is_press)
{
  uint32_t key_keycode, modifier_keycode;
  uint64_t now = ei_now (ei_client->ei);

  g_debug ("%s", __func__);

  if (!ei_client->ei_connected || !ei_client->has_keyboard)
    {
      g_warning ("EI keyboard device not available");
      return FALSE;
    }

  if (!keysym_to_keycode (ei_client->xkb_keymap,
                          ei_client->xkb_state,
                          keysym,
                          &key_keycode,
                          &modifier_keycode))
    {
      g_warning ("Error transforming keysym to keycode");
      return FALSE;
    }

  if (is_press && key_keycode != XKB_KEY_NoSymbol)
    {
      ei_device_keyboard_key (ei_client->keyboard, modifier_keycode, is_press);
      ei_device_frame (ei_client->keyboard, now);
    }

  ei_device_keyboard_key (ei_client->keyboard, key_keycode, is_press);
  ei_device_frame (ei_client->keyboard, now);

  if (!is_press && key_keycode != XKB_KEY_NoSymbol)
    {
      ei_device_keyboard_key (ei_client->keyboard, modifier_keycode, is_press);
      ei_device_frame (ei_client->keyboard, now);
    }

  return TRUE;
}

gboolean
gpd_ei_client_notify_pointer_button (GpdEiClient *ei_client,
                                     int32_t      button,
                                     gboolean     is_press)
{
  g_debug ("%s", __func__);

  if (!ei_client->ei_connected || !ei_client->has_pointer)
    {
      g_warning ("EI pointer device not available");
      return FALSE;
    }

  ei_device_button_button (ei_client->pointer, button, is_press);
  ei_device_frame (ei_client->pointer, ei_now (ei_client->ei));

  return TRUE;
}

gboolean
gpd_ei_client_notify_pointer_motion_absolute (GpdEiClient *ei_client,
                                              double       x,
                                              double       y)
{
  g_debug ("%s", __func__);

  if (!ei_client->ei_connected || !ei_client->has_pointer)
    {
      g_warning ("EI pointer device not available");
      return FALSE;
    }

  ei_device_pointer_motion_absolute (ei_client->pointer, x, y);
  ei_device_frame (ei_client->pointer, ei_now (ei_client->ei));

  return TRUE;
}
