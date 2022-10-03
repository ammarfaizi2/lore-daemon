# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import discord
from discord.ext import commands
from discord import Intents
from dscord.config import ACTIVITY_NAME

from dscord.database import DB


class GWClient(commands.Bot):
	def __init__(self, db_conn) -> None:
		self.db = DB(db_conn)
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
