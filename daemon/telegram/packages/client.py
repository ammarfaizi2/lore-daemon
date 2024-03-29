# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

import logging
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union
from email.message import Message

from atom import utils
from enums import Platform
from telegram import config
from telegram.database import DB
from .decorator import handle_flood
from exceptions import DaemonException


log = logging.getLogger("telegram")


class DaemonTelegram(Client):
	def __init__(self, name: str, api_id: int,
		api_hash: str, conn, **kwargs
	):
		super().__init__(name, api_id,
				api_hash, **kwargs)
		self.db = DB(conn)


	async def report_err(self, e: DaemonException):
		capt = f"Atom URL: {e.atom_url}\n"
		capt += f"Thread URL: {e.thread_url}"
		log.warning(e.original_exception)
		await self.send_log_file(capt)


	@handle_flood
	async def send_log_file(self, caption: str):
		for handler in log.root.handlers:
			if isinstance(handler, logging.FileHandler):
				filename = handler.baseFilename

		await self.send_document(
			config.LOG_CHANNEL_ID,
			filename,
			caption=caption
		)


	@handle_flood
	async def send_text_email(
		self,
		chat_id: Union[int, str],
		text: str,
		reply_to: int,
		url: str = None,
		parse_mode: ParseMode = ParseMode.HTML
	) -> Message:
		log.debug("[send_text_email]")
		return await self.send_message(
			chat_id=chat_id,
			text=text,
			reply_to_message_id=reply_to,
			parse_mode=parse_mode,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)


	@handle_flood
	async def send_patch_email(
		self,
		mail: Message,
		chat_id: Union[int, str],
		text: str,
		reply_to: int,
		url: str = None,
		parse_mode: ParseMode = ParseMode.HTML
	) -> Message:
		log.debug("[send_patch_email]")
		tmp, doc, caption, url = utils.prepare_patch(
			mail, text, url, Platform.TELEGRAM
		)
		m = await self.send_document(
			chat_id=chat_id,
			document=doc,
			caption=caption,
			reply_to_message_id=reply_to,
			parse_mode=parse_mode,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)

		utils.remove_patch(tmp)
		return m
