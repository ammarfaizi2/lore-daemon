# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands
from discord import Interaction
from discord import app_commands

from atom import utils
from atom import Scraper
from enums import Platform
from exceptions import DaemonException


class GetLoreSC(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot = bot


	@app_commands.command(
		name="lore",
		description="Get lore email from raw email URL."
	)
	@app_commands.describe(url="Raw lore email URL")
	async def get_lore(self, i: "Interaction", url: str):
		s = Scraper()

		try:
			mail = await s.get_email_from_url(url)
			text, _, is_patch = utils.create_template(mail, Platform.DISCORD)
		except:
			e = DaemonException()
			e.set_thread_url(url)
			e.set_message(utils.catch_err())
			await self.bot.report_err(e)
			return

		if is_patch:
			m = await self.bot.send_patch_mail_interaction(
				mail=mail, i=i, text=text, url=url
			)
		else:
			text = "#ml\n" + text
			m = await self.bot.send_text_mail_interaction(
				i=i, text=text, url=url
			)
