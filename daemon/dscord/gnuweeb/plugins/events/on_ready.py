# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import logging
from discord.ext import commands


log = logging.getLogger("dscord")

class OnReady(commands.Cog):
	def __init__(self, bot: "commands.Bot") -> None:
		self.bot = bot


	@commands.Cog.listener()
	async def on_ready(self):
		self.bot.mailer.run()
		prefix = self.bot.command_prefix[0]

		t = "[ GNU/Weeb Bot is connected ]\n\n"
		t += f"ID   : {self.bot.user.id}\n"
		t += f"Name : {self.bot.user.display_name}\n"
		t += f"Tags : {self.bot.user}\n\n"
		t += f"Send `{prefix}sync` message to the Discord channel "
		t += "where the bot is running.\n"

		log.info(t)
