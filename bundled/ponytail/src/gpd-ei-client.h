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

#ifndef GPD_EI_CLIENT_H
#define GPD_EI_CLIENT_H

#include <glib-object.h>

#include "gpd.h"
#include "gpd-dbus-remote-desktop.h"

#define GPD_TYPE_EI_CLIENT (gpd_ei_client_get_type ())
G_DECLARE_FINAL_TYPE (GpdEiClient,
                      gpd_ei_client,
                      GPD, EI_CLIENT,
                      GObject);

/**
 * gpd_ei_client_new:
 * @session_proxy: a proxy to the remote desktop D-Bus interface
 *
 * Creates a new #GpdEiClient. To start the connection to EIS, call
 * #gpd_ei_client_start.
 *
 * Return: A new #GpdEiClient
 */
GpdEiClient *gpd_ei_client_new (GpdDBusRemoteDesktopSession *session_proxy);

/**
 * gpd_ei_client_start:
 * @ei_client: A #GpdEiClient created with #gpd_ei_client_new
 *
 * Starts the connection to EIS. Once this function is called, 3 different
 * signals could be emitted:
 *
 * - error: A fatal error was encountered connecting to EIS
 * - connected: Successfully connected to EIS
 * - disconnected: Disconnected from EIS after a successful connection
 */
void gpd_ei_client_start (GpdEiClient *ei_client);

/**
 * gpd_ei_client_is_connected:
 * @ei_client: A #GpdEiClient
 *
 * Return: Whether the connection is established or not
 */
gboolean gpd_ei_client_is_connected (GpdEiClient *ei_client);

/**
 * gpd_ei_client_has_keyboard:
 * @ei_client: A #GpdEiClient
 *
 * Return: Whether a keyboard device is available or not
 */
gboolean gpd_ei_client_has_keyboard (GpdEiClient *ei_client);

/**
 * gpd_ei_client_has_pointer:
 * @ei_client: A #GpdEiClient
 *
 * Return: Whether a pointer device is available or not
 */
gboolean gpd_ei_client_has_pointer (GpdEiClient *ei_client);

/**
 * gpd_ei_client_notify_keyboard_keycode:
 * @ei_client: A connected #GpdEiClient
 * @keycode: evdev key code as defined in linux/input-event-codes.h.
 * @is_press: TRUE for key press, FALSE for key release
 *
 * Sends a key event
 *
 * Return: FALSE on error
 */
gboolean gpd_ei_client_notify_keyboard_keycode (GpdEiClient *ei_client,
                                                guint        keycode,
                                                gboolean     is_press);

/**
 * gpd_ei_client_notify_keyboard_keysym:
 * @ei_client: A connected #GpdEiClient
 * @keycode: Keysym
 * @is_press: TRUE for key press, FALSE for key release
 *
 * Sends a keysym
 *
 * Return: FALSE on error
 */
gboolean gpd_ei_client_notify_keyboard_keysym (GpdEiClient *ei_client,
                                               guint        keysym,
                                               gboolean     is_press);

/**
 * gpd_ei_client_notify_pointer_button:
 * @ei_client: A connected #GpdEiClient
 * @button: Button code
 * @is_press: TRUE for button press, FALSE for button release
 *
 * Sends a pointer button event
 *
 * Return: FALSE on error
 */
gboolean gpd_ei_client_notify_pointer_button (GpdEiClient *ei_client,
                                              int32_t      button,
                                              gboolean     is_press);

/**
 * gpd_ei_client_notify_pointer_motion_absolute:
 * @ei_client: A connected #GpdEiClient
 * @x: Absolute X coordinate
 * @y: Absolute Y coordinate
 *
 * Sends an absolute pointer motion event
 *
 * Return: FALSE on error
 */
gboolean gpd_ei_client_notify_pointer_motion_absolute (GpdEiClient *ei_client,
                                                       double       x,
                                                       double       y);

#endif /* GPD_EI_CLIENT_H */
