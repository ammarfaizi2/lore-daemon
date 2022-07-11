# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from .database import Database

from scrapper import Scrapper, utils

from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import shutil, asyncio

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
		s = Scrapper(database=self.db)

		for thread, url, msg_id in await s.see_new_thread():
			email = self.db.get_email(msg_id)
			reply_to = None
			in_reply_to = thread.get("in-reply-to")

			if email:
				continue

			if in_reply_to:
				in_reply_id = utils.extract_email_id(str(in_reply_to))
				reply_to = self.db.reply_to(in_reply_id)

			template, files = utils.create_template(thread)

			m = await self.client.send_message(
				-1001673279485,
				template,
				reply_to_message_id=reply_to,
				parse_mode=enums.ParseMode.HTML,
				reply_markup=InlineKeyboardMarkup([
					[InlineKeyboardButton(
						"See the full message",
						url=url
					)]
				])
			)

			for d, f in files:
				await m.reply_document(f"{d}/{f}", file_name=f)
				await asyncio.sleep(1) # use sleep to avoid telegram flood

			if files:
				shutil.rmtree(str(files[0][0]))

			email_id = self.db.insert_email(msg_id)
			self.db.insert_telegram(email_id, m.chat.id, m.id)

			await asyncio.sleep(10) # use sleep to avoid telegram flood

	def listen_for_new_thread(self):
		# Schedule job every 5 seconds in interval
		self.job.add_job(
			self.__listening,
			trigger='interval',
			seconds=5
		)
