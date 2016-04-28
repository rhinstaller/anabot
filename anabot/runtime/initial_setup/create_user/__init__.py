# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('anabot')

from anabot.runtime.decorators import handle_action, handle_check

_local_path = '/initial_setup/create_user'
handle_act = lambda x,y: handle_action(_local_path + x, y)
handle_chck = lambda x,y: handle_check(_local_path + x, y)

# user spoke should be the same as in anaconda installer
# we will reuse handlers and checks (but with different XML tree)

from anabot.runtime.installation.configuration import create_user as cu

handle_act('', cu.user_spoke_handler)

handle_act('/full_name', cu.user_full_name_handler)
handle_chck('/full_name', cu.user_full_name_check)

handle_act('/username', cu.user_username_handler)
handle_chck('/username', cu.user_username_check)

handle_act('/is_admin', cu.user_is_admin_handler)
handle_chck('/is_admin', cu.user_is_admin_check)

handle_act('/require_password', cu.user_require_passwd_handler)
handle_chck('/require_password', cu.user_require_passwd_check)

handle_act('/password', cu.user_password_handler)

handle_act('/confirm_password', cu.user_confirm_password_handler)

handle_act('/done', cu.user_done_handler)

# advanced dialog
cua = cu.advanced

handle_act('/advanced', cua.user_advanced_handler)
handle_chck('/advanced', cua.user_advanced_check)

handle_act('/advanced/home', cua.user_adv_homedir_handler)
handle_chck('/advanced/home', cua.user_adv_homedir_check)

handle_act('/advanced/manual_uid', cua.user_adv_manual_uid_handler)
handle_chck('/advanced/manual_uid', cua.user_adv_manual_uid_check)

handle_act('/advanced/uid', cua.user_adv_uid_handler)

handle_act('/advanced/manual_gid', cua.user_adv_manual_gid_handler)
handle_chck('/advanced/manual_gid', cua.user_adv_manual_gid_check)

handle_act('/advanced/gid', cua.user_adv_gid_handler)

handle_act('/advanced/groups', cua.user_adv_groups_handler)

handle_act('/advanced/cancel', cua.user_adv_cancel_handler)
handle_chck('/advanced/cancel', cua.user_adv_cancel_check)

handle_act('/advanced/save', cua.user_adv_save_handler)
handle_chck('/advanced/save', cua.user_adv_save_check)

