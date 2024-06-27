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

#include "gpd-stream.h"
#include "gpd-context.h"

enum
{
  READY,
  CLOSED,

  N_SIGNALS
};

static guint signals[N_SIGNALS];

typedef struct _GpdStreamPrivate
{
  GpdContext *context;

  uint32_t pipewire_node_id;

  GpdDBusScreenCastStream *proxy;
} GpdStreamPrivate;

G_DEFINE_TYPE_WITH_PRIVATE (GpdStream, gpd_stream, G_TYPE_OBJECT)

uint32_t
gpd_stream_get_pipewire_node_id (GpdStream *stream)
{
  GpdStreamPrivate *priv = gpd_stream_get_instance_private (stream);

  return priv->pipewire_node_id;
}

const char *
gpd_stream_get_object_path (GpdStream *stream)
{
  GpdStreamPrivate *priv = gpd_stream_get_instance_private (stream);

  return g_dbus_proxy_get_object_path (G_DBUS_PROXY (priv->proxy));
}

static void
on_pipewire_stream_added (GpdDBusScreenCastStream *proxy,
                          unsigned int             node_id,
                          GpdStream               *stream)
{
  GpdStreamPrivate *priv = gpd_stream_get_instance_private (stream);

  priv->pipewire_node_id = (uint32_t) node_id;

  g_signal_emit (stream, signals[READY], 0);
}

GpdStream *
gpd_stream_new (GpdContext              *context,
                GpdDBusScreenCastStream *proxy)
{
  GpdStream *stream;
  GpdStreamPrivate *priv;

  stream = g_object_new (GPD_TYPE_STREAM, NULL);
  priv = gpd_stream_get_instance_private (stream);

  priv->context = context;
  priv->proxy = proxy;
  g_signal_connect (proxy, "pipewire-stream-added",
                    G_CALLBACK (on_pipewire_stream_added),
                    stream);

  return stream;
}

static void
gpd_stream_finalize (GObject *object)
{
  GpdStream *stream = GPD_STREAM (object);
  GpdStreamPrivate *priv = gpd_stream_get_instance_private (stream);

  g_clear_object (&priv->proxy);

  G_OBJECT_CLASS (gpd_stream_parent_class)->finalize (object);
}

static void
gpd_stream_init (GpdStream *stream)
{
}

static void
gpd_stream_class_init (GpdStreamClass *klass)
{
  GObjectClass *object_class = G_OBJECT_CLASS (klass);

  object_class->finalize = gpd_stream_finalize;

  signals[READY] = g_signal_new ("ready",
                                 G_TYPE_FROM_CLASS (klass),
                                 G_SIGNAL_RUN_LAST,
                                 0,
                                 NULL, NULL, NULL,
                                 G_TYPE_NONE, 0);
  signals[CLOSED] = g_signal_new ("closed",
                                  G_TYPE_FROM_CLASS (klass),
                                  G_SIGNAL_RUN_LAST,
                                  0,
                                  NULL, NULL, NULL,
                                  G_TYPE_NONE, 0);
}
