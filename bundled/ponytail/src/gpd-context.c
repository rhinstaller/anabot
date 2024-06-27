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
	
#include "gpd-dbus-remote-desktop.h"
#include "gpd-dbus-screen-cast.h"
#include "gpd-context.h"
#include "gpd.h"

struct _GpdContext
{
  GObject parent;

  GMainContext *main_context;

  GpdDBusRemoteDesktop *remote_desktop_proxy;
  GpdDBusScreenCast *screen_cast_proxy;

  GList *sessions;
};

G_DEFINE_TYPE (GpdContext, gpd_context, G_TYPE_OBJECT);

GpdDBusRemoteDesktop *
gpd_context_get_remote_desktop_proxy (GpdContext *context)
{
  return context->remote_desktop_proxy;
}

GpdDBusScreenCast *
gpd_context_get_screen_cast_proxy (GpdContext *context)
{
  return context->screen_cast_proxy;
}

void
gpd_context_set_remote_desktop_proxy (GpdContext           *context,
                                      GpdDBusRemoteDesktop *proxy)
{
  context->remote_desktop_proxy = proxy;
}

void
gpd_context_set_screen_cast_proxy (GpdContext        *context,
                                   GpdDBusScreenCast *proxy)
{
  context->screen_cast_proxy = proxy;
}

GMainContext *
gpd_context_get_main_context (GpdContext *context)
{
  return context->main_context;
}

static void
on_session_stopped (GpdSession *session,
                    GpdContext *context)
{
  context->sessions = g_list_remove (context->sessions, session);
}

void
gpd_context_add_session (GpdContext *context,
                         GpdSession *session)
{
  context->sessions = g_list_append (context->sessions, session);
  g_signal_connect (session, "stopped",
                    G_CALLBACK (on_session_stopped), context);
}

GList *
gpd_context_get_sessions (GpdContext *context)
{
  return context->sessions;
}

static void
gpd_context_init (GpdContext *context)
{
  context->main_context = g_main_context_default ();
}

static void
gpd_context_class_init (GpdContextClass *klass)
{
}
