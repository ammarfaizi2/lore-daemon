# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands


class OnReady(commands.Cog):
	def __init__(self, bot: "commands.Bot") -> None:
		self.bot = bot


	@commands.Cog.listener()
	async def on_ready(self):
		t = "[ GNU/Weeb Bot is connected ]\n\n"
		t += f"ID   : {self.bot.user.id}\n"
		t += f"Name : {self.bot.user.display_name}\n"
		t += f"Tags : {self.bot.user}\n\n"
		t += "Ready to get the latest of lore kernel emails."
		print(t)
