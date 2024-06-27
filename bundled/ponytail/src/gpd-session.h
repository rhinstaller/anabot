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

#ifndef GPD_SESSION_H
#define GPD_SESSION_H

#include <glib-object.h>
#include <stdint.h>

#include "gpd.h"

#define GPD_TYPE_SESSION (gpd_session_get_type ())
G_DECLARE_DERIVABLE_TYPE (GpdSession, gpd_session, GPD, SESSION, GObject);

struct _GpdSessionClass
{
  GObjectClass parent_class;

  void (*stream_ready) (GpdSession *session,
                        GpdStream  *stream);
  void (*stop) (GpdSession *session);
};

GpdContext *gpd_session_get_context (GpdSession *session);

gboolean gpd_session_connect_monitor (GpdSession *session,
                                      const char *connector);

gboolean gpd_session_connect_window (GpdSession *session,
                                     uint64_t    window_id);

gboolean gpd_session_notify_keyboard_keysym (GpdSession *session,
                                             uint32_t    keysym,
                                             gboolean    state);

gboolean gpd_session_notify_keyboard_keycode (GpdSession *session,
                                              guint       keycode,
                                              gboolean    state);

gboolean gpd_session_notify_pointer_button (GpdSession    *session,
                                            int32_t        button,
                                            gboolean       state);

gboolean gpd_session_notify_pointer_motion_absolute (GpdSession *session,
                                                     double      x,
                                                     double      y);

void gpd_session_start (GpdSession *session);

void gpd_session_stop (GpdSession *session);

void gpd_session_restart (GpdSession *session);

#endif /* GPD_SESSION_H */
