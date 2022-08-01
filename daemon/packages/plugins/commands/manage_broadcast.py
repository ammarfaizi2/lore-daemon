# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram.types import Message
from pyrogram import filters, enums
from packages import DaemonClient


@DaemonClient.on_message(
	filters.command("add_bc") &
	(filters.private | filters.group)
)
async def add_broadcast(c: DaemonClient, m: Message):
	if m.chat.type == enums.ChatType.PRIVATE:
		chat_name = m.chat.first_name
	else:
		chat_name = m.chat.title

	inserted = c.db.insert_broadcast(
		chat_id=m.chat.id,
		name=chat_name,
		type=str(m.chat.type),
		created_at=m.date,
		username=m.chat.username,
		link=m.chat.invite_link
	)

	if inserted is None:
		msg = f"This chat already added for receiving email messages"
	else:
		msg = f"Success add this chat for receiving email messages"

	await m.reply(msg)
