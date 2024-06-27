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

#ifndef GPD_CONTEXT_H
#define GPD_CONTEXT_H

#include <glib-object.h>

#include "gpd-dbus-remote-desktop.h"
#include "gpd-dbus-screen-cast.h"
#include "gpd.h"

#define GPD_TYPE_CONTEXT (gpd_context_get_type ())
G_DECLARE_FINAL_TYPE (GpdContext, gpd_context, GPD, CONTEXT, GObject);

GpdDBusRemoteDesktop * gpd_context_get_remote_desktop_proxy (GpdContext *context);

GpdDBusScreenCast * gpd_context_get_screen_cast_proxy (GpdContext *context);

void gpd_context_set_remote_desktop_proxy (GpdContext           *context,
                                           GpdDBusRemoteDesktop *proxy);

void gpd_context_set_screen_cast_proxy (GpdContext        *context,
                                        GpdDBusScreenCast *proxy);

GMainContext *gpd_context_get_main_context (GpdContext *context);

void gpd_context_add_session (GpdContext *context,
                              GpdSession *session);

GList * gpd_context_get_sessions (GpdContext *context);

#endif /* GPD_CONTEXT_H */
