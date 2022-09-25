# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands


class OnError(commands.Cog):
	def __init__(self, bot: "commands.Bot") -> None:
		self.bot = bot


	@commands.Cog.listener()
	async def on_command_error(self, _, err):
		if isinstance(err, commands.CommandNotFound):
			pass
