# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from packages import DaemonClient
from scraper import utils
from pyrogram.types import CallbackQuery
import config


@DaemonClient.on_callback_query(config.admin_only, group=2)
async def on_del_chat(c: DaemonClient, cb: CallbackQuery):
	if not "del_chat" in cb.data:
		return

	chats = c.db.get_broadcast_chats()
	if not bool(chats):
		return await cb.answer("Currently empty.")

	index = int(utils.remove_command(cb.data))
	chat = chats[index - 1]
	chat_id = chat[1]
	chat_name = chat[3]

	success = c.db.delete_broadcast(chat_id)
	if not success:
		msg = f"Failed to delete {chat_name} from receiving email message\n"
		msg += "Maybe it's already been deleted or not exists."
	else:
		msg = f"Success delete {chat_name} from receiving email message"

	await cb.answer(msg, show_alert=True)

	await cb.message.delete()
	if cb.message.reply_to_message:
		await cb.message.reply_to_message.delete()
