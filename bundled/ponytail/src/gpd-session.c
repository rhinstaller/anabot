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

#include <glib-object.h>

#include "config.h"
#include "gpd-dbus-remote-desktop.h"
#include "gpd-context.h"
#include "gpd-stream.h"
#include "gpd-session.h"
#include "gpd.h"

#if GPD_HAS_LIBEI
  #include "gpd-ei-client.h"
#endif

enum
{
  PROP_0,

  PROP_CONTEXT,
};

enum
{
  ACQUIRED,
  STOPPED,

  LAST_SIGNAL
};

static guint signals[LAST_SIGNAL];

typedef struct _GpdSessionPrivate
{
  GpdContext *context;

  GpdDBusRemoteDesktopSession *remote_desktop_session;
  GpdDBusScreenCastSession *screen_cast_session;

  GpdStream *stream;

  GCancellable *cancellable;

  gboolean started;
  gboolean connected;
  GAsyncResult *start_session_res;

#if GPD_HAS_LIBEI
  GpdEiClient *ei_client;
#endif
} GpdSessionPrivate;

G_DEFINE_TYPE_WITH_PRIVATE (GpdSession, gpd_session, G_TYPE_OBJECT);

GpdContext *
gpd_session_get_context (GpdSession *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);

  return priv->context;
}

static void
on_stream_ready (GpdStream  *stream,
                 GpdSession *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  g_debug ("%s", __func__);
  priv->connected = TRUE;
  
  if (priv->started && GPD_SESSION_GET_CLASS (session)->stream_ready)
    GPD_SESSION_GET_CLASS (session)->stream_ready (session, stream);
}

static void
on_stream_closed (GpdStream  *stream,
                  GpdSession *session)
{
  g_debug ("%s", __func__);
  gpd_session_restart (session);
}

static void
finish_start_session (GpdSession *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *proxy = priv->remote_desktop_session;
  GAsyncResult *result = priv->start_session_res;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);
  if (!gpd_dbus_remote_desktop_session_call_start_finish (proxy,
                                                          result,
                                                          &error))
    {
      g_warning ("Failed to start session: %s", error->message);
      g_object_unref (result);

      gpd_session_stop (session);

      return;
    }

  g_object_unref (result);
  priv->started = TRUE;

  if (priv->connected && GPD_SESSION_GET_CLASS (session)->stream_ready)
    GPD_SESSION_GET_CLASS (session)->stream_ready (session, priv->stream);
}

#if GPD_HAS_LIBEI
static void
on_ei_client_connected (GpdEiClient *ei_client,
                        GpdSession *session)
{
  g_debug ("%s", __func__);
  finish_start_session (session);
}

static void
on_ei_client_disconnected (GpdEiClient *ei_client,
                           GpdSession *session)
{
  g_debug ("%s", __func__);
  gpd_session_restart (session);
}

static void
on_ei_client_error (GpdEiClient *ei_client,
                    GpdSession *session)
{
  g_debug ("%s", __func__);
  /* For backwards compatibility, if the connection to EIS fails, the session is
   * set as `started` but `ei_connected` is set as `FALSE`, falling back to the
   * Mutter D-Bus backend. */
  finish_start_session (session);
}
#endif

static void
on_session_start_finished (GObject      *object,
                           GAsyncResult *result,
                           gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *proxy = priv->remote_desktop_session;
  priv->start_session_res = g_object_ref (result);

#if GPD_HAS_LIBEI
  priv->ei_client = gpd_ei_client_new (proxy);
  g_signal_connect (priv->ei_client,
                    "connected",
                    G_CALLBACK (on_ei_client_connected),
                    session);
  g_signal_connect (priv->ei_client,
                    "disconnected",
                    G_CALLBACK (on_ei_client_disconnected),
                    session);
  g_signal_connect (priv->ei_client,
                    "error",
                    G_CALLBACK (on_ei_client_error),
                    session);
  gpd_ei_client_start (priv->ei_client);
#else
  finish_start_session (session);
#endif
}

static void
start_session (GpdSession *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *proxy = priv->remote_desktop_session;

  g_debug ("%s", __func__);
  gpd_dbus_remote_desktop_session_call_start (proxy,
                                              priv->cancellable,
                                              on_session_start_finished,
                                              session);
}

static void
on_screen_cast_stream_proxy_acquired (GObject      *object,
                                      GAsyncResult *result,
                                      gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusScreenCastStream *stream_proxy;
  g_autoptr (GError) error = NULL;
  GpdStream *stream;

  g_debug ("%s", __func__);
  stream_proxy = gpd_dbus_screen_cast_stream_proxy_new_finish (result, &error);
  if (!stream_proxy)
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
        g_debug ("%s was canceled", __func__);
      else
        g_warning ("Failed to acquire stream proxy: %s", error->message);

      gpd_session_stop (session);

      return;
    }

  stream = gpd_stream_new (priv->context, stream_proxy);
  g_signal_connect (stream, "ready", G_CALLBACK (on_stream_ready),
                    session);
  g_signal_connect (stream, "closed", G_CALLBACK (on_stream_closed),
                    session);
  priv->stream = stream;

  start_session (session);
}

static void
on_record_window_finished (GObject      *object,
                           GAsyncResult *result,
                           gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusScreenCastSession *proxy = priv->screen_cast_session;
  g_autofree char *stream_path = NULL;
  g_autoptr (GError) error = NULL;
  GDBusConnection *connection;

  g_debug ("%s", __func__);
  if (!gpd_dbus_screen_cast_session_call_record_window_finish (proxy,
                                                               &stream_path,
                                                               result,
                                                               &error))
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
        g_debug ("%s was canceled", __func__);
      else
        g_warning ("Failed to record window: %s", error->message);

      gpd_session_restart (session);

      return;
    }

  connection = g_dbus_proxy_get_connection (G_DBUS_PROXY (proxy));
  gpd_dbus_screen_cast_stream_proxy_new (connection,
                                         G_DBUS_PROXY_FLAGS_NONE,
                                         MUTTER_SCREEN_CAST_BUS_NAME,
                                         stream_path,
                                         priv->cancellable,
                                         on_screen_cast_stream_proxy_acquired,
                                         session);
}

static void
on_record_monitor_finished (GObject      *object,
                            GAsyncResult *result,
                            gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusScreenCastSession *proxy = priv->screen_cast_session;
  g_autofree char *stream_path = NULL;
  g_autoptr (GError) error = NULL;
  GDBusConnection *connection;

  g_debug ("%s", __func__);
  if (!gpd_dbus_screen_cast_session_call_record_monitor_finish (proxy,
                                                                &stream_path,
                                                                result,
                                                                &error))
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
        g_debug ("%s was canceled", __func__);
      else
        g_warning ("Failed to record monitor: %s", error->message);

      gpd_session_restart (session);

      return;
    }

  connection = g_dbus_proxy_get_connection (G_DBUS_PROXY (proxy));
  gpd_dbus_screen_cast_stream_proxy_new (connection,
                                         G_DBUS_PROXY_FLAGS_NONE,
                                         MUTTER_SCREEN_CAST_BUS_NAME,
                                         stream_path,
                                         priv->cancellable,
                                         on_screen_cast_stream_proxy_acquired,
                                         session);
}

static void
on_screen_cast_session_proxy_acquired (GObject      *object,
                                       GAsyncResult *result,
                                       gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusScreenCastSession *session_proxy;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);
  session_proxy =
    gpd_dbus_screen_cast_session_proxy_new_finish (result, &error);
  if (!session_proxy)
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
          g_debug ("%s was canceled", __func__);
      else
        {
          g_warning ("Failed to acquire screen cast session proxy: %s\n",
                     error->message);
        }

      gpd_session_stop (session);

      return;
    }

  priv->screen_cast_session = session_proxy;
  g_signal_emit (session, signals[ACQUIRED], 0);
}

static void
on_screen_cast_session_created (GObject      *source_object,
                                GAsyncResult *res,
                                gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusScreenCast *screen_cast_proxy;
  g_autofree char *session_path = NULL;
  g_autoptr (GError) error = NULL;
  GDBusConnection *connection;

  g_debug ("%s", __func__);
  screen_cast_proxy = gpd_context_get_screen_cast_proxy (priv->context);
  if (!gpd_dbus_screen_cast_call_create_session_finish (screen_cast_proxy,
                                                        &session_path,
                                                        res,
                                                        &error))
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
        g_debug ("%s was canceled", __func__);
      else
        g_warning ("Failed to start screen cast session: %s\n", error->message);

      gpd_session_stop (session);

      return;
    }

  connection = g_dbus_proxy_get_connection (G_DBUS_PROXY (screen_cast_proxy));
  gpd_dbus_screen_cast_session_proxy_new (connection,
                                          G_DBUS_PROXY_FLAGS_NONE,
                                          MUTTER_SCREEN_CAST_BUS_NAME,
                                          session_path,
                                          priv->cancellable,
                                          on_screen_cast_session_proxy_acquired,
                                          session);
}

static void
on_remote_desktop_session_closed (GpdDBusRemoteDesktopSession *session_proxy,
                                  GpdSession                  *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);

  g_debug ("%s", __func__);
  g_clear_object (&priv->remote_desktop_session);
  g_clear_object (&priv->screen_cast_session);

  gpd_session_restart (session);
}

static void
on_remote_desktop_session_proxy_acquired (GObject      *object,
                                          GAsyncResult *result,
                                          gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *session_proxy;
  g_autoptr (GError) error = NULL;
  const char *remote_desktop_session_id;
  GpdDBusScreenCast *screen_cast_proxy;
  GVariantBuilder properties_builder;
  GVariant *properties_variant;

  g_debug ("%s", __func__);
  session_proxy =
    gpd_dbus_remote_desktop_session_proxy_new_finish (result, &error);
  if (!session_proxy)
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
        g_debug ("%s was canceled", __func__);
      else
        {
          g_warning ("Failed to acquire remote desktop session proxy: %s\n",
                     error->message);
        }

      gpd_session_stop (session);

      return;
    }

  g_signal_connect (session_proxy, "closed",
                    G_CALLBACK (on_remote_desktop_session_closed),
                    session);

  priv->remote_desktop_session = session_proxy;

  remote_desktop_session_id =
    gpd_dbus_remote_desktop_session_get_session_id (session_proxy);

  g_variant_builder_init (&properties_builder, G_VARIANT_TYPE ("a{sv}"));
  g_variant_builder_add (&properties_builder, "{sv}",
                         "remote-desktop-session-id",
                         g_variant_new_string (remote_desktop_session_id));
  properties_variant = g_variant_builder_end (&properties_builder);

  screen_cast_proxy = gpd_context_get_screen_cast_proxy (priv->context);
  gpd_dbus_screen_cast_call_create_session (screen_cast_proxy,
                                            properties_variant,
                                            priv->cancellable,
                                            on_screen_cast_session_created,
                                            session);
}

static void
on_remote_desktop_session_created (GObject      *source_object,
                                   GAsyncResult *res,
                                   gpointer      user_data)
{
  GpdSession *session = user_data;
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktop *remote_desktop_proxy;
  g_autofree char *session_path = NULL;
  GDBusConnection *connection;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);
  remote_desktop_proxy = gpd_context_get_remote_desktop_proxy (priv->context);
  if (!gpd_dbus_remote_desktop_call_create_session_finish (remote_desktop_proxy,
                                                           &session_path,
                                                           res,
                                                           &error))
    {
      if (priv->cancellable && g_cancellable_is_cancelled (priv->cancellable))
        g_debug ("%s was canceled", __func__);
      else
        {
          g_warning ("Failed to start remote desktop session: %s\n",
                     error->message);
        }

      gpd_session_stop (session);

      return;
    }

  connection = g_dbus_proxy_get_connection (G_DBUS_PROXY (remote_desktop_proxy));
  gpd_dbus_remote_desktop_session_proxy_new (connection,
                                             G_DBUS_PROXY_FLAGS_NONE,
                                             MUTTER_REMOTE_DESKTOP_BUS_NAME,
                                             session_path,
                                             priv->cancellable,
                                             on_remote_desktop_session_proxy_acquired,
                                             session);
}

static void
gpd_session_dispose (GObject *object)
{
  GpdSession *session = GPD_SESSION (object);
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);

  g_debug ("%s", __func__);
  g_clear_object (&priv->stream);

  G_OBJECT_CLASS (gpd_session_parent_class)->dispose (object);
}

static void
gpd_session_finalize (GObject *object)
{
  GpdSession *session = GPD_SESSION (object);
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);

  g_debug ("%s", __func__);
  g_assert (!priv->remote_desktop_session);

  if (priv->cancellable)
    g_cancellable_cancel (priv->cancellable);
  g_clear_object (&priv->cancellable);

  G_OBJECT_CLASS (gpd_session_parent_class)->finalize (object);
}

static void
gpd_session_set_property (GObject      *object,
                          guint         prop_id,
                          const GValue *value,
                          GParamSpec   *pspec)
{
  GpdSession *session = GPD_SESSION (object);
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);

  g_debug ("%s", __func__);
  switch (prop_id)
    {
    case PROP_CONTEXT:
      priv->context = g_value_get_object (value);
      break;

    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
    }
}

static void
gpd_session_get_property (GObject    *object,
                          guint       prop_id,
                          GValue     *value,
                          GParamSpec *pspec)
{
  GpdSession *session = GPD_SESSION (object);
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);

  g_debug ("%s", __func__);
  switch (prop_id)
    {
    case PROP_CONTEXT:
      g_value_set_object (value, priv->context);

    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
    }
}

static void
gpd_session_init (GpdSession *session)
{
  g_debug ("%s", __func__);
}

static void
gpd_session_class_init (GpdSessionClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);

  g_debug ("%s", __func__);
  object_class->dispose = gpd_session_dispose;
  object_class->finalize = gpd_session_finalize;
  object_class->set_property = gpd_session_set_property;
  object_class->get_property = gpd_session_get_property;

  g_object_class_install_property (object_class,
                                   PROP_CONTEXT,
                                   g_param_spec_object ("context",
                                                        "GpdContext",
                                                        "The GpdContext instance",
                                                        GPD_TYPE_CONTEXT,
                                                        G_PARAM_READWRITE |
                                                        G_PARAM_CONSTRUCT_ONLY |
                                                        G_PARAM_STATIC_STRINGS));

  signals[ACQUIRED] = g_signal_new ("acquired",
                                   G_TYPE_FROM_CLASS (klass),
                                   G_SIGNAL_RUN_LAST,
                                   0,
                                   NULL, NULL, NULL,
                                   G_TYPE_NONE, 0);

  signals[STOPPED] = g_signal_new ("stopped",
                                   G_TYPE_FROM_CLASS (klass),
                                   G_SIGNAL_RUN_LAST,
                                   0,
                                   NULL, NULL, NULL,
                                   G_TYPE_NONE, 0);
}

gboolean
gpd_session_connect_monitor (GpdSession *session,
                             const char *connector)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GVariantBuilder properties_variant;

  g_debug ("%s", __func__);
  if (priv->connected)
    {
      g_warning ("A session is already active");
      return FALSE;
    }

  g_variant_builder_init (&properties_variant, G_VARIANT_TYPE ("a{sv}"));
  gpd_dbus_screen_cast_session_call_record_monitor (priv->screen_cast_session,
                                                    connector,
                                                    g_variant_builder_end (&properties_variant),
                                                    priv->cancellable,
                                                    on_record_monitor_finished,
                                                    session);

  return TRUE;
}

gboolean
gpd_session_connect_window (GpdSession *session,
                            uint64_t    window_id)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GVariantBuilder properties_variant;

  g_debug ("%s", __func__);
  if (priv->connected)
    {
      g_warning ("A session is already active");
      return FALSE;
    }

  g_variant_builder_init (&properties_variant, G_VARIANT_TYPE ("a{sv}"));
  g_variant_builder_add (&properties_variant, "{sv}",
                         "window-id",
                         g_variant_new_uint64 (window_id));
  gpd_dbus_screen_cast_session_call_record_window (priv->screen_cast_session,
                                                   g_variant_builder_end (&properties_variant),
                                                   priv->cancellable,
                                                   on_record_window_finished,
                                                   session);

  return TRUE;
}

gboolean
gpd_session_notify_keyboard_keycode (GpdSession *session,
                                     guint       keycode,
                                     gboolean    state)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *session_proxy = priv->remote_desktop_session;

  g_debug ("%s", __func__);
  if (!priv->connected)
    {
      g_warning ("Not connected");
      return FALSE;
    }

#if GPD_HAS_LIBEI
  if (gpd_ei_client_is_connected (priv->ei_client) &&
      gpd_ei_client_has_keyboard (priv->ei_client))
    return gpd_ei_client_notify_keyboard_keycode (priv->ei_client, keycode, state);
#endif

  gpd_dbus_remote_desktop_session_call_notify_keyboard_keycode (session_proxy,
                                                                keycode,
                                                                state,
                                                                NULL,
                                                                NULL,
                                                                NULL);

  return TRUE;
}

gboolean
gpd_session_notify_keyboard_keysym (GpdSession *session,
                                    uint32_t    keysym,
                                    gboolean    state)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *session_proxy = priv->remote_desktop_session;

  g_debug ("%s", __func__);
  if (!priv->connected)
    {
      g_warning ("Not connected");
      return FALSE;
    }

#if GPD_HAS_LIBEI
  if (gpd_ei_client_is_connected (priv->ei_client) &&
      gpd_ei_client_has_keyboard (priv->ei_client))
    return gpd_ei_client_notify_keyboard_keysym (priv->ei_client, keysym, state);
#endif

  gpd_dbus_remote_desktop_session_call_notify_keyboard_keysym (session_proxy,
                                                               keysym,
                                                               state,
                                                               NULL,
                                                               NULL,
                                                               NULL);

  return TRUE;
}

gboolean
gpd_session_notify_pointer_button (GpdSession *session,
                                   int32_t     button,
                                   gboolean    state)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *session_proxy = priv->remote_desktop_session;

  g_debug ("%s", __func__);
  if (!priv->connected)
    {
      g_warning ("Not connected");
      return FALSE;
    }

#if GPD_HAS_LIBEI
  if (gpd_ei_client_is_connected (priv->ei_client) &&
      gpd_ei_client_has_pointer (priv->ei_client))
    return gpd_ei_client_notify_pointer_button (priv->ei_client, button, state);
#endif

  gpd_dbus_remote_desktop_session_call_notify_pointer_button (session_proxy,
                                                              button,
                                                              state,
                                                              NULL,
                                                              NULL,
                                                              NULL);

  return TRUE;
}

gboolean
gpd_session_notify_pointer_motion_absolute (GpdSession *session,
                                            double      x,
                                            double      y)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *session_proxy = priv->remote_desktop_session;
  const char *stream_path;

  g_debug ("%s", __func__);
  if (!priv->connected)
    {
      g_warning ("Not connected");
      return FALSE;
    }

#if GPD_HAS_LIBEI
  if (gpd_ei_client_is_connected (priv->ei_client) &&
      gpd_ei_client_has_pointer (priv->ei_client))
      return gpd_ei_client_notify_pointer_motion_absolute (priv->ei_client, x, y);
#endif

  stream_path = gpd_stream_get_object_path (priv->stream);
  if (!stream_path)
    {
      g_warning ("Failed to retrieve stream path");
      return FALSE;
    }

  gpd_dbus_remote_desktop_session_call_notify_pointer_motion_absolute (session_proxy,
                                                                       stream_path,
                                                                       x,
                                                                       y,
                                                                       NULL,
                                                                       NULL,
                                                                       NULL);

  return TRUE;
}

void
gpd_session_start (GpdSession *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktop *remote_desktop_proxy;

  g_debug ("%s", __func__);
  priv->cancellable = g_cancellable_new ();

  remote_desktop_proxy = gpd_context_get_remote_desktop_proxy (priv->context);
  gpd_dbus_remote_desktop_call_create_session (remote_desktop_proxy,
                                               priv->cancellable,
                                               on_remote_desktop_session_created,
                                               session);
}

void
gpd_session_stop (GpdSession *session)
{
  GpdSessionPrivate *priv = gpd_session_get_instance_private (session);
  GpdDBusRemoteDesktopSession *proxy = priv->remote_desktop_session;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);
  if (priv->cancellable)
    g_cancellable_cancel (priv->cancellable);

  if (GPD_SESSION_GET_CLASS (session)->stop)
    GPD_SESSION_GET_CLASS (session)->stop (session);

  if (proxy && priv->started)
    {
      if (!gpd_dbus_remote_desktop_session_call_stop_sync (proxy, NULL, &error))
        g_warning ("Failed to stop: %s", error->message);
    }

  g_clear_object (&priv->remote_desktop_session);
  g_clear_object (&priv->screen_cast_session);
#if GPD_HAS_LIBEI
  g_clear_object (&priv->ei_client);
#endif
  g_signal_emit (session, signals[STOPPED], 0);

  priv->started = FALSE;
  priv->connected = FALSE;
}

void gpd_session_restart (GpdSession *session)
{
  g_debug ("%s", __func__);
  gpd_session_stop (session);
  gpd_session_start (session);
}
