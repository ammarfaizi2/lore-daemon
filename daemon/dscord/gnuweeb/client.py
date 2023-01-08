# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import discord
from discord import Interaction
from discord.ext import commands
from discord import Intents
from typing import Union

from . import filters
from . import models
from atom import utils
from enums import Platform
from exceptions import DaemonException
from logger.log import BotLogger
from dscord.config import ACTIVITY_NAME, LOG_CHANNEL_ID
from dscord.database import DB


class GWClient(commands.Bot):
	def __init__(self, db_conn, logger: BotLogger) -> None:
		self.db = DB(db_conn)
		intents = Intents.default()
		intents.message_content = True
		self.mailer = None
		self.logger = logger
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


	async def report_err(self, e: DaemonException):
		self.logger.warning(e.original_exception)
		capt = f"Atom URL: {e.atom_url}\n"
		capt += f"Thread URL: {e.thread_url}"
		await self.send_log_file(capt)


	@filters.wait_on_limit
	async def send_log_file(self, caption: str):
		filename = self.logger.handlers[0].baseFilename
		channel = self.get_channel(LOG_CHANNEL_ID)
		await channel.send(
			content=caption,
			file=discord.File(filename)
		)


	@filters.wait_on_limit
	async def send_text_email(self, guild_id: int, chat_id: int, text: str,
				reply_to: Union[int, None] = None, url: str = None):
		self.logger.debug("[send_text_email]")
		channel = self.get_channel(chat_id)

		return await channel.send(
			content=text,
			reference=discord.MessageReference(
				guild_id=guild_id,
				channel_id=chat_id,
				message_id=reply_to
			) if reply_to else None,
			view=models.FullMessageBtn(url)
		)


	@filters.wait_on_limit
	async def send_patch_email(self, mail, guild_id: int, chat_id: int, text: str,
				reply_to: Union[int, None] = None, url: str = None):
		self.logger.debug("[send_patch_email]")
		tmp, doc, caption, url = utils.prepare_patch(
			mail, text, url, Platform.DISCORD
		)
		channel = self.get_channel(chat_id)

		m = await channel.send(
			content=caption,
			file=discord.File(doc),
			reference=discord.MessageReference(
				guild_id=guild_id,
				channel_id=chat_id,
				message_id=reply_to
			) if reply_to else None,

			view=models.FullMessageBtn(url)
		)

		utils.remove_patch(tmp)
		return m


	async def send_text_mail_interaction(self, i: "Interaction",
					text: str, url: str = None):
		return await i.response.send_message(
			content=text,
			view=models.FullMessageBtn(url)
		)


	async def send_patch_mail_interaction(self, mail, i: "Interaction",
						text: str, url: str = None):
		tmp, doc, caption, url = utils.prepare_patch(
			mail, text, url, Platform.DISCORD
		)
		m = await i.response.send_message(
			content=caption,
			file=discord.File(doc),
			view=models.FullMessageBtn(url)
		)
		utils.remove_patch(tmp)
		return m
