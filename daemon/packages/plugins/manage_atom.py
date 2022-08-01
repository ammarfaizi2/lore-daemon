# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram.types import Message
from pyrogram import filters
from packages import DaemonClient
from scraper import utils

@DaemonClient.on_message(
	filters.command("add_atom") &
	filters.chat(["kiizuah", "nekoha", -1001673279485])
)
async def add_atom_url(c: DaemonClient, m: Message):
	if len(m.command) <= 1:
		tutor = "Please specify the URL\n"
		tutor += "Example: `/add_atom https://lore.kernel.org/linux-sgx/new.atom`"
		return await m.reply(tutor)

	text = utils.remove_command(m.text)
	is_atom = await utils.is_atom_url(text)
	if not is_atom:
		return await m.reply("Invalid Atom URL")

	inserted = c.db.insert_atom(text)
	if inserted is None:
		return await m.reply(f"This URL already listened for new email.")

	await m.reply(f"Success add **{text}** for listening new email")
