# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import discord
from discord.ext import commands
from discord import Intents
from dscord.config import ACTIVITY_NAME


class GWClient(commands.Bot):
	def __init__(self) -> None:
		intents = Intents.default()
		intents.message_content = True
		super().__init__(
			command_prefix=["$", "."],
			description="Just a bot for receiving lore emails.",
			intents=intents,
			activity=discord.Game(ACTIVITY_NAME)
		)


	async def setup_hook(self):
		await self.load_extension(
			name=".gnuweeb.plugins",
			package="dscord"
		)
