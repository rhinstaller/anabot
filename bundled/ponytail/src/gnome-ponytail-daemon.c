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

#include <gio/gio.h>
#include <glib/gi18n.h>
#include <stdio.h>
#include <stdlib.h>

#include "gpd-context.h"
#include "gpd-dbus-remote-desktop.h"
#include "gpd-session.h"
#include "gpd-event-controller.h"
#include "gpd.h"

typedef struct _GpdApp
{
  GApplication parent;

  GCancellable *cancellable;
  guint remote_desktop_watch_name_id;
  guint screen_cast_watch_name_id;

  GpdContext *context;
  GpdEventController *event_controller;

} GpdApp;


#define GPD_TYPE_APP (gpd_app_get_type ())
G_DECLARE_FINAL_TYPE (GpdApp, gpd_app, GPD, APP, GApplication);
G_DEFINE_TYPE (GpdApp, gpd_app, G_TYPE_APPLICATION)

static void
on_remote_desktop_proxy_acquired (GObject      *object,
                                  GAsyncResult *result,
                                  gpointer      user_data)
{
  GpdApp *app = user_data;
  GpdDBusRemoteDesktop *proxy;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);
  proxy = gpd_dbus_remote_desktop_proxy_new_for_bus_finish (result, &error);
  if (!proxy)
    {
      g_warning ("Failed to create remote desktop proxy: %s", error->message);
      return;
    }

  gpd_context_set_remote_desktop_proxy (app->context, proxy);

  if (gpd_context_get_screen_cast_proxy (app->context))
    gpd_session_start (GPD_SESSION (app->event_controller));
}

static void
on_screen_cast_proxy_acquired (GObject      *object,
                               GAsyncResult *result,
                               gpointer      user_data)
{
  GpdApp *app = user_data;
  GpdDBusScreenCast *proxy;
  g_autoptr (GError) error = NULL;

  g_debug ("%s", __func__);
  proxy = gpd_dbus_screen_cast_proxy_new_for_bus_finish (result, &error);
  if (!proxy)
    {
      g_warning ("Failed to create screen cast proxy: %s", error->message);
      return;
    }

  gpd_context_set_screen_cast_proxy (app->context, proxy);
  app->event_controller = gpd_event_controller_new (app->context);

  if (gpd_context_get_remote_desktop_proxy (app->context))
    gpd_session_start (GPD_SESSION (app->event_controller));
}

static void
on_remote_desktop_name_appeared (GDBusConnection *connection,
                                 const char      *name,
                                 const char      *name_owner,
                                 gpointer         user_data)
{
  GpdApp *app = user_data;

  g_debug ("%s", __func__);
  gpd_dbus_remote_desktop_proxy_new_for_bus (G_BUS_TYPE_SESSION,
                                             G_DBUS_PROXY_FLAGS_NONE,
                                             MUTTER_REMOTE_DESKTOP_BUS_NAME,
                                             MUTTER_REMOTE_DESKTOP_OBJECT_PATH,
                                             app->cancellable,
                                             on_remote_desktop_proxy_acquired,
                                             app);
}

static void
on_remote_desktop_name_vanished (GDBusConnection *connection,
                                 const char      *name,
                                 gpointer         user_data)
{
  GpdApp *app = user_data;

  g_debug ("%s", __func__);
  if (gpd_context_get_remote_desktop_proxy (app->context))
    gpd_session_stop (GPD_SESSION (app->event_controller));

  gpd_context_set_remote_desktop_proxy (app->context, NULL);
}

static void
on_screen_cast_name_appeared (GDBusConnection *connection,
                              const char      *name,
                              const char      *name_owner,
                              gpointer         user_data)
{
  GpdApp *app = user_data;

  g_debug ("%s", __func__);
  gpd_dbus_screen_cast_proxy_new_for_bus (G_BUS_TYPE_SESSION,
                                          G_DBUS_PROXY_FLAGS_NONE,
                                          MUTTER_SCREEN_CAST_BUS_NAME,
                                          MUTTER_SCREEN_CAST_OBJECT_PATH,
                                          app->cancellable,
                                          on_screen_cast_proxy_acquired,
                                          app);
}

static void
on_screen_cast_name_vanished (GDBusConnection *connection,
                              const char      *name,
                              gpointer         user_data)
{
  GpdApp *app = user_data;

  g_debug ("%s", __func__);
  if (gpd_context_get_screen_cast_proxy (app->context))
    gpd_session_stop (GPD_SESSION (app->event_controller));

  gpd_context_set_screen_cast_proxy (app->context, NULL);
}

static void
gpd_app_init (GpdApp *app)
{
}

static void
gpd_app_startup (GApplication *app)
{
  GpdApp *gpd_app = GPD_APP (app);

  g_debug ("%s", __func__);
  gpd_app->context = g_object_new (GPD_TYPE_CONTEXT, NULL);

  gpd_app->remote_desktop_watch_name_id =
    g_bus_watch_name (G_BUS_TYPE_SESSION,
                      MUTTER_REMOTE_DESKTOP_BUS_NAME,
                      G_BUS_NAME_WATCHER_FLAGS_NONE,
                      on_remote_desktop_name_appeared,
                      on_remote_desktop_name_vanished,
                      app, NULL);

  gpd_app->screen_cast_watch_name_id =
    g_bus_watch_name (G_BUS_TYPE_SESSION,
                      MUTTER_SCREEN_CAST_BUS_NAME,
                      G_BUS_NAME_WATCHER_FLAGS_NONE,
                      on_screen_cast_name_appeared,
                      on_screen_cast_name_vanished,
                      app, NULL);

  gpd_app->cancellable = g_cancellable_new ();

  g_application_hold (app);

  G_APPLICATION_CLASS (gpd_app_parent_class)->startup (app);
}

static void
gpd_app_shutdown (GApplication *app)
{
  GpdApp *gpd_app = GPD_APP (app);

  g_debug ("%s", __func__);
  g_cancellable_cancel (gpd_app->cancellable);
  g_clear_object (&gpd_app->cancellable);

  gpd_context_set_remote_desktop_proxy (gpd_app->context, NULL);
  g_bus_unwatch_name (gpd_app->remote_desktop_watch_name_id);
  gpd_app->remote_desktop_watch_name_id = 0;

  gpd_context_set_screen_cast_proxy (gpd_app->context, NULL);
  g_bus_unwatch_name (gpd_app->screen_cast_watch_name_id);
  gpd_app->screen_cast_watch_name_id = 0;

  G_APPLICATION_CLASS (gpd_app_parent_class)->shutdown (app);
}

static void
gpd_app_class_init (GpdAppClass *klass)
{
  GApplicationClass *g_application_class = G_APPLICATION_CLASS (klass);

  g_debug ("%s", __func__);
  g_application_class->startup = gpd_app_startup;
  g_application_class->shutdown = gpd_app_shutdown;
}

int
main (int argc, char **argv)
{
  g_autoptr(GApplication) app = NULL;
  g_autoptr(GOptionContext) option_context = NULL;

  g_debug ("%s", __func__);
  g_set_application_name ("GNOME Ponytail Daemon");

  app = g_object_new (GPD_TYPE_APP,
                      "application-id", "org.gnome.PonytailDaemon",
                      "flags", G_APPLICATION_IS_SERVICE,
                      NULL);

  return g_application_run (app, argc, argv);
}
