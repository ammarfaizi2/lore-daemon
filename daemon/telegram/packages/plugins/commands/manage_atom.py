# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram.types import Message
from pyrogram import filters
from packages import DaemonClient
from scraper import utils
import config


@DaemonClient.on_message(
	filters.command("add_atom") &
	config.admin_only
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


@DaemonClient.on_message(
	filters.command("del_atom") &
	config.admin_only
)
async def del_atom_url(c: DaemonClient, m: Message):
	atoms = c.db.get_atom_urls()
	if len(atoms) == 0:
		return await m.reply("Currently empty.")

	text = "List of atom URL that currently listened:\n"
	for u,i in zip(atoms, range(1, len(atoms)+1)):
		text += f"{i}. {u}\n"

	text += "\nChoose one of the URL above to delete by index below."
	await m.reply(text, reply_markup=utils.button_numbers(
		data=atoms,
		callback_prefix="del_atom"
	))
