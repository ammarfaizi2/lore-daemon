# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from packages import DaemonClient
from scraper import utils
from pyrogram.types import CallbackQuery
import config


@DaemonClient.on_callback_query(config.admin_only, group=1)
async def on_del_atom(c: DaemonClient, cb: CallbackQuery):
	if not "del_atom" in cb.data:
		return

	atoms = c.db.get_atom_urls()
	if len(atoms) == 0:
		return await cb.answer("Currently empty.")

	index = int(utils.remove_command(cb.data))
	atom = atoms[index - 1]
	c.db.delete_atom(atom)

	await cb.answer(
		f"Success delete {atom} from listening new email",
		show_alert=True
	)

	await cb.message.delete()
	if cb.message.reply_to_message:
		await cb.message.reply_to_message.delete()
