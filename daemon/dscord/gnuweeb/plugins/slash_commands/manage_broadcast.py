# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands
from discord import Interaction
from discord import app_commands

from atom import utils
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


	@broadcast.command(
		name="add",
		description="Add broadcast channel for sending lore emails."
	)
	@filters.lore_admin
	async def add_channel(self, i: "Interaction"):
		inserted = self.bot.db.save_broadcast(
			guild_id=i.guild_id,
			channel_id=i.channel_id,
			channel_name=i.channel.name,
			channel_link=utils.channel_link(
				guild_id=i.guild_id,
				channel_id=i.channel_id
			)
		)

		if inserted is None:
			t = f"This channel already added for send email messages."
			await i.response.send_message(t, ephemeral=True)
			return

		t = f"Success add this channel for send email messages."
		await i.response.send_message(t, ephemeral=True)


	@broadcast.command(
		name="delete",
		description="Delete broadcast channel from sending email messages."
	)
	@filters.lore_admin
	async def del_channel(self, i: "Interaction"):
		success = self.bot.db.delete_broadcast(i.channel_id)
		if not success:
			t = "Failed to delete this channel\n"
			t += "Maybe because already deleted or not exists."
			await i.response.send_message(t, ephemeral=True)
			return

		t = f"Success delete this channel from sending email messages."
		await i.response.send_message(t, ephemeral=True)
