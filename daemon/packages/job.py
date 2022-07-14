# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from .database import Database

from scrapper import Scrapper, utils

from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from filelock import FileLock
import shutil, asyncio, os

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

		for thread, url, email_msg_id in await s.see_new_thread():
			await self.handle_msg(thread, url, email_msg_id)

	async def handle_msg(self, thread, url, email_msg_id):
		#
		# TODO(ammarfaizi2): Broadcast to several @tg_chat_ids.
		#
		tg_chat_ids = [
			os.getenv("TG_SEND_TO")
		]

		for i in tg_chat_ids:
			await self.__handle_msg(thread, url, email_msg_id, i)
			await asyncio.sleep(1)

	async def __handle_msg(self, thread, url, email_msg_id, tg_chat_id):
		email_id = self.db.need_to_send_to_tg(email_msg_id, tg_chat_id)
		if not email_id:
			return

		text, files = utils.create_template(thread)
		reply_to = self.db.get_tg_reply_to(email_id, tg_chat_id)

		m = await self.send_to_tg(tg_chat_id, text, reply_to, url)
		self.db.insert_telegram(email_id, m.chat.id, m.id)

		for d, f in files:
			await m.reply_document(f"{d}/{f}", file_name=f)
			await asyncio.sleep(1)

		if files:
			shutil.rmtree(str(files[0][0]))

		await asyncio.sleep(10)

	async def send_to_tg(self, tg_chat_id, text, reply_to, url):
		return await self.client.send_message(
			tg_chat_id,
			text,
			reply_to_message_id=reply_to,
			parse_mode=enums.ParseMode.HTML,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)

	def listen_for_new_thread(self):
		# Schedule job every 5 seconds in interval
		self.job.add_job(
			self.__listening,
			trigger='interval',
			seconds=5
		)
