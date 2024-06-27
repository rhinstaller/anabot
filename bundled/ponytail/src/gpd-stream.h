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

#ifndef GPD_STREAM_H
#define GPD_STREAM_H

#include <glib-object.h>
#include <stdint.h>

#include "gpd-dbus-screen-cast.h"
#include "gpd.h"

#define GPD_TYPE_STREAM (gpd_stream_get_type ())
G_DECLARE_DERIVABLE_TYPE (GpdStream, gpd_stream, GPD, STREAM, GObject)

struct _GpdStreamClass
{
  GObjectClass parent_class;
};

uint32_t gpd_stream_get_pipewire_node_id (GpdStream *stream);

const char * gpd_stream_get_object_path (GpdStream *stream);

GpdStream * gpd_stream_new (GpdContext              *context,
                            GpdDBusScreenCastStream *proxy);

#endif /* GPD_STREAM_H */
