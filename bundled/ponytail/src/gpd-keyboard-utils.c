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
#include <glib.h>
#include <linux/input-event-codes.h>

#include "gpd-keyboard-utils.h"

typedef enum _EvdevButtonType
{
  EVDEV_BUTTON_TYPE_NONE,
  EVDEV_BUTTON_TYPE_KEY,
  EVDEV_BUTTON_TYPE_BUTTON,
} EvdevButtonType;

uint32_t
xkb_keycode_to_evdev (uint32_t xkb_keycode)
{
  /* XKB adds a fixed offset of 8, evdev doesn't have that offset */
  return xkb_keycode - 8;
}

#if GPD_HAS_LIBEI
static gboolean
setup_xkb_keymap (struct ei_keymap    *keymap,
                  struct xkb_context **out_xkb_context,
                  struct xkb_keymap  **out_xkb_keymap,
                  struct xkb_state   **out_xkb_state,
                  GError             **error)
{
  struct xkb_context *xkb_context = NULL;
  struct xkb_keymap *xkb_keymap = NULL;
  struct xkb_state *xkb_state = NULL;
  size_t keymap_size;
  g_autofree char *buf = NULL;

  xkb_context = xkb_context_new (XKB_CONTEXT_NO_FLAGS);
  if (!xkb_context)
    {
      g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                   "Failed to create XKB context");
      goto err;
    }

  keymap_size = ei_keymap_get_size (keymap);
  buf = g_malloc0 (keymap_size + 1);
  while (TRUE)
    {
      int ret;

      ret = read (ei_keymap_get_fd (keymap), buf, keymap_size);
      if (ret > 0)
        {
          break;
        }
      else if (ret == 0)
        {
          g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                       "Keyboard layout was empty");
          goto err;
        }
      else if (errno == EINTR)
        {
          continue;
        }
      else
        {
          g_set_error (error, G_IO_ERROR, g_io_error_from_errno (errno),
                       "Failed to read layout: %s", g_strerror (errno));
          goto err;
        }
    }

  xkb_keymap = xkb_keymap_new_from_string (xkb_context, buf,
                                           XKB_KEYMAP_FORMAT_TEXT_V1,
                                           XKB_KEYMAP_COMPILE_NO_FLAGS);
  if (!xkb_keymap)
    {
      g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                   "Failed to create XKB keymap");
      goto err;
    }

  xkb_state = xkb_state_new (xkb_keymap);
  if (!xkb_state)
    {
      g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                   "Failed to create XKB state");
      goto err;
    }

  *out_xkb_context = xkb_context;
  *out_xkb_keymap = xkb_keymap;
  *out_xkb_state = xkb_state;
  return TRUE;

err:
  g_clear_pointer (&xkb_state, xkb_state_unref);
  g_clear_pointer (&xkb_keymap, xkb_keymap_unref);
  g_clear_pointer (&xkb_context, xkb_context_unref);
  return FALSE;
}

gboolean
process_ei_keyboard (struct ei_device    *device,
                     struct xkb_context **out_xkb_context,
                     struct xkb_keymap  **out_xkb_keymap,
                     struct xkb_state   **out_xkb_state,
                     GError             **error)
{
  struct ei_keymap *keymap;
  enum ei_keymap_type type;

  keymap = ei_device_keyboard_get_keymap (device);
  if (!keymap)
    return TRUE;

  type = ei_keymap_get_type (keymap);
  switch (type)
    {
    case EI_KEYMAP_TYPE_XKB:
      return setup_xkb_keymap (keymap,
                               out_xkb_context,
                               out_xkb_keymap,
                               out_xkb_state,
                               error);
    default:
      g_set_error (error, G_IO_ERROR, G_IO_ERROR_FAILED,
                   "Unknown keyboard layout type");
      return FALSE;
    }

  return TRUE;
}

static gboolean
pick_keycode_for_keysym_in_current_group (struct xkb_keymap *xkb_keymap,
                                          struct xkb_state  *xkb_state,
                                          uint32_t           keysym,
                                          uint32_t          *keycode_out,
                                          uint32_t          *level_out)
{
  uint32_t keycode, layout;
  xkb_keycode_t min_keycode, max_keycode;

  layout = xkb_state_serialize_layout (xkb_state, XKB_STATE_LAYOUT_EFFECTIVE);
  min_keycode = xkb_keymap_min_keycode (xkb_keymap);
  max_keycode = xkb_keymap_max_keycode (xkb_keymap);
  for (keycode = min_keycode; keycode < max_keycode; keycode++)
    {
      int num_levels, level;

      num_levels = xkb_keymap_num_levels_for_key (xkb_keymap, keycode, layout);
      for (level = 0; level < num_levels; level++)
        {
          const xkb_keysym_t *syms;
          int num_syms, sym;

          num_syms = xkb_keymap_key_get_syms_by_level (xkb_keymap, keycode,
                                                       layout, level, &syms);
          for (sym = 0; sym < num_syms; sym++)
            {
              if (syms[sym] == keysym)
                {
                  *keycode_out = keycode;
                  if (level_out)
                    *level_out = level;
                  return TRUE;
                }
            }
        }
    }

  return FALSE;
}

static EvdevButtonType
get_button_type (uint16_t code)
{
  switch (code)
    {
    case BTN_TOOL_PEN:
    case BTN_TOOL_RUBBER:
    case BTN_TOOL_BRUSH:
    case BTN_TOOL_PENCIL:
    case BTN_TOOL_AIRBRUSH:
    case BTN_TOOL_MOUSE:
    case BTN_TOOL_LENS:
    case BTN_TOOL_QUINTTAP:
    case BTN_TOOL_DOUBLETAP:
    case BTN_TOOL_TRIPLETAP:
    case BTN_TOOL_QUADTAP:
    case BTN_TOOL_FINGER:
    case BTN_TOUCH:
      return EVDEV_BUTTON_TYPE_NONE;
    }

  if (code >= KEY_ESC && code <= KEY_MICMUTE)
    return EVDEV_BUTTON_TYPE_KEY;
  if (code >= BTN_MISC && code <= BTN_GEAR_UP)
    return EVDEV_BUTTON_TYPE_BUTTON;
  if (code >= KEY_OK && code <= KEY_LIGHTS_TOGGLE)
    return EVDEV_BUTTON_TYPE_KEY;
  if (code >= BTN_DPAD_UP && code <= BTN_DPAD_RIGHT)
    return EVDEV_BUTTON_TYPE_BUTTON;
  if (code >= KEY_ALS_TOGGLE && code <= KEY_KBDINPUTASSIST_CANCEL)
    return EVDEV_BUTTON_TYPE_KEY;
  if (code >= BTN_TRIGGER_HAPPY && code <= BTN_TRIGGER_HAPPY40)
    return EVDEV_BUTTON_TYPE_BUTTON;
  return EVDEV_BUTTON_TYPE_NONE;
}

static gboolean
get_level_modifiers (struct xkb_keymap *xkb_keymap,
                     struct xkb_state  *xkb_state,
                     uint32_t           level,
                     uint32_t          *keycode_out)
{
  uint32_t keysym, keycode;

  if (level == 0)
    {
      *keycode_out = XKB_KEY_NoSymbol;
      return TRUE;
    }

  if (level == 1)
    {
      keysym = XKB_KEY_Shift_L;
    }
  else if (level == 2)
    {
      keysym = XKB_KEY_ISO_Level3_Shift;
    }
  else
    {
      g_warning ("Unhandled level: %d", level);
      return FALSE;
    }

  if (!pick_keycode_for_keysym_in_current_group (xkb_keymap, xkb_state, keysym,
                                                 &keycode, NULL))
    return FALSE;

  *keycode_out = xkb_keycode_to_evdev (keycode);
  return TRUE;
}

gboolean
keysym_to_keycode (struct xkb_keymap *xkb_keymap,
                   struct xkb_state  *xkb_state,
                   uint32_t           keysym,
                   uint32_t          *key_keycode_out,
                   uint32_t          *modifier_keycode_out)
{
  uint32_t key_keycode = 0, modifier_keycode = 0, level = 0, evcode = 0;

  if (!xkb_state)
    return FALSE;

  if (!pick_keycode_for_keysym_in_current_group (xkb_keymap,
                                                 xkb_state,
                                                 keysym,
                                                 &key_keycode,
                                                 &level))
    {
      g_warning ("No keycode found for keyval %x in current group", keysym);
      return FALSE;
    }

  evcode = xkb_keycode_to_evdev (key_keycode);
  if (get_button_type (evcode) != EVDEV_BUTTON_TYPE_KEY)
    {
      g_warning ("Unknown/invalid key 0x%x pressed", evcode);
      return FALSE;
    }

  if (!get_level_modifiers (xkb_keymap,
                            xkb_state,
                            level,
                            &modifier_keycode))
    {
      g_warning ("No modifier keycode found for keyval %x", keysym);
      return FALSE;
    }

  *key_keycode_out = evcode;
  *modifier_keycode_out = modifier_keycode;
  return TRUE;
}
#endif /* GPD_HAS_LIBEI */
