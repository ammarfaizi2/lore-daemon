# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands


class SyncCommand(commands.Cog):
	def __init__(self, bot: "commands.Bot") -> None:
		self.bot = bot


	@commands.command("sync", aliases=["s"])
	@commands.is_owner()
	async def sync_it(self, ctx: "commands.Context"):
		self.bot.tree.copy_global_to(guild=ctx.guild)
		s = await self.bot.tree.sync(guild=ctx.guild)

		await ctx.send(f"Synced {len(s)} commands.")
