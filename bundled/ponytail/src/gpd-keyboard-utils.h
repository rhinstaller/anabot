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

#ifndef GPD_KEYBOARD_UTILS_H
#define GPD_KEYBOARD_UTILS_H

#include "config.h"
#include <stdint.h>

#if GPD_HAS_LIBEI
#include <libei.h>
#include <xkbcommon/xkbcommon.h>
#endif

/**
 * xkb_keycode_to_evdev:
 * @xkb_keycode: The XKB keycode
 *
 * Transforms a XKB keycode to a evdev keycode
 *
 * Return: The evdev keycode
 */
uint32_t xkb_keycode_to_evdev (uint32_t xkb_keycode);

#if GPD_HAS_LIBEI
/**
 * process_ei_keyboard:
 * @device: libei device
 * @out_xkb_context: Returned XKB context
 * @out_xkb_keymap: Returned XKB keymap
 * @out_xkb_state: Returned XKB state
 * @error: If the function returns FALSE, the error reason
 *
 * Returns a XKB context, keymap and state for a libei keyboard
 *
 * Return: FALSE on error, TRUE otherwise
 */
gboolean process_ei_keyboard (struct ei_device    *device,
                              struct xkb_context **out_xkb_context,
                              struct xkb_keymap  **out_xkb_keymap,
                              struct xkb_state   **out_xkb_state,
                              GError             **error);

/**
 * keysym_to_keycode:
 * @xkb_keymap: Keymap
 * @xkb_state: Keyboard state
 * @keysym: Keysym to transform
 * @key_keycode_out: Returned keycode
 * @modifier_keycode_out: Returned modifier keycode, can be XKB_KEY_NoSymbol
 *
 * Transforms a keysym to a keycode and its modifier keycode.
 *
 * Return: FALSE on error, TRUE otherwise
 */
gboolean keysym_to_keycode (struct xkb_keymap *xkb_keymap,
                            struct xkb_state  *xkb_state,
                            uint32_t           keysym,
                            uint32_t          *key_keycode_out,
                            uint32_t          *modifier_keycode_out);
#endif /* GPD_HAS_LIBEI */

#endif /* GPD_KEYBOARD_UTILS_H */
