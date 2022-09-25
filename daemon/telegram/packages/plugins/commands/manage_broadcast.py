# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram.types import Message
from pyrogram import filters, enums
from telegram.packages import DaemonClient
from telegram.scraper import utils
from telegram import config


@DaemonClient.on_message(
	filters.command("add_bc") &
	config.admin_only
)
async def add_broadcast(c: DaemonClient, m: Message):
	if m.chat.type == enums.ChatType.PRIVATE:
		chat_name = m.chat.first_name
	else:
		chat_name = m.chat.title

	inserted = c.db.save_broadcast(
		chat_id=m.chat.id,
		name=chat_name,
		type=str(m.chat.type),
		created_at=m.date,
		username=m.chat.username,
		link=utils.create_chat_link(m.chat)
	)

	if inserted is None:
		msg = f"This chat already added for receiving email messages"
	else:
		msg = f"Success add this chat for receiving email messages"

	await m.reply(msg)


@DaemonClient.on_message(
	filters.command("del_bc") &
	config.admin_only
)
async def del_broadcast(c: DaemonClient, m: Message):
	if "--list" in m.text:
		chats = c.db.get_broadcast_chats()
		if len(chats) == 0:
			return await m.reply("Currently empty.")

		text = "List of chats that will receive email message:\n"
		for u,i in zip(chats, range(1, len(chats)+1)):
			text += f"{i}. **[{u[3]}]({u[5]})**\n"

		text += "\nChoose one of the chat above to delete by index below."
		return await m.reply(
			text=text,
			disable_web_page_preview=True,
			reply_markup=utils.button_numbers(
				data=chats,
				callback_prefix="del_chat"
			)
		)

	success = c.db.delete_broadcast(m.chat.id)
	if not success:
		msg = "Failed to delete this chat from receiving email message\n"
		msg += "Maybe it's already been deleted or not exists."
	else:
		msg = "Success delete this chat from receiving email message"

	await m.reply(msg)
