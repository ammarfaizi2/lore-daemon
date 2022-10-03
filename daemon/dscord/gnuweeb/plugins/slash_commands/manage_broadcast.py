# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands
from discord import Interaction
from discord import app_commands

from dscord.gnuweeb import filters


class ManageBroadcastSC(commands.Cog):
	broadcast = app_commands.Group(
		name="broadcast",
		description="Manage broadcast channel."
	)


	def __init__(self, bot) -> None:
		self.bot = bot


	@broadcast.command(
		name="list",
		description="List of broadcast channel."
	)
	@filters.lore_admin
	async def list_channel(self, i: "Interaction"):
		chats = self.bot.db.get_broadcast_chats()
		if len(chats) == 0:
			t = "Currently empty."
			await i.response.send_message(t, ephemeral=True)
			return

		text = "List of channels that will send email messages:\n"
		for u,n in zip(chats, range(1, len(chats)+1)):
			text += f"{n}. **{u[3]}**\n"
			text += f"Link: {u[4]}\n\n"

		await i.response.send_message(text, ephemeral=True)
