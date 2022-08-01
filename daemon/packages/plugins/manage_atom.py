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
	text = utils.remove_command(m.text)
	if not utils.is_atom_url(text):
		return

	###
	### TODO: Muhammad Rizki: Add atom url into the database
	###
