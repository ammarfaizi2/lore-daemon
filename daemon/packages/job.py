# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from .database import Database
from .database.structs import Emails, TGEmails

from scrapper import Scrapper, utils

from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from typing import Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

class Job():
	def __init__(
		self,
		client:Client,
		job:AsyncIOScheduler,
		database:Database
	):
		self.job = job
		self.client = client
		self.db = database

	async def __listening(self):
		s = Scrapper()
		thread, thread_url = await s.see_new_thread()

		msg_id = (
			thread.get("message-id", "")
			.replace("<", "")
			.replace(">", "")
		)

		in_reply_to = (
			thread.get("in-reply-to", "")
			.replace("<", "")
			.replace(">", "")
		)

		email: Union["Emails", None] = (
			self.db.get_email(msg_id)
		)

		if not email:
			if in_reply_to:
				reply_email: Union["TGEmails", None] = (
					self.db.reply_to(in_reply_to)
				)

				if reply_email:
					reply_to = reply_email.tg_msg_id
				else:
					reply_to = None

			template, files = utils.create_template(thread)

			m = await self.client.send_message(
				-1001673279485,
				template,
				reply_to_message_id=reply_to,
				parse_mode=enums.ParseMode.HTML,
				reply_markup=InlineKeyboardMarkup([
					[InlineKeyboardButton(
						"See the full message",
						url=thread_url.replace("/raw","")
					)]
				])
			)

			for f in files:
				await m.reply_document(f, file_name=f, quote=True)
				os.remove(f)

			email_id = self.db.insert_email(msg_id)
			self.db.insert_telegram(email_id, m.chat.id, m.id)

	def listen_for_new_thread(self):
		# Schedule job every 5 seconds in interval
		self.job.add_job(
			self.__listening,
			trigger='interval',
			seconds=5
		)
