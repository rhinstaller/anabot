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

#ifndef GPD_EVENT_CONTROLLER_H
#define GPD_EVENT_CONTROLLER_H

#include <glib.h>

#include "gpd-session.h"
#include "gpd-dbus-event-controller.h"
#include "gpd.h"

#define GPD_TYPE_EVENT_CONTROLLER (gpd_event_controller_get_type ())
G_DECLARE_FINAL_TYPE (GpdEventController,
                      gpd_event_controller,
                      GPD, EVENT_CONTROLLER,
                      GpdSession);

GpdEventController *gpd_event_controller_new (GpdContext *context);

#endif /* GPD_EVENT_CONTROLLER_H */

