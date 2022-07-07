# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from scrapper import Scrapper, utils

from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

class Job():
	def __init__(self, client:Client, job:AsyncIOScheduler):
		self.job = job
		self.client = client

	async def __listening(self):
		s = Scrapper()
		thread, thread_url = await s.see_new_thread()

		template, files = utils.create_template(thread)

		m = await self.client.send_message(
			"kiizuah",
			template,
			parse_mode=enums.ParseMode.HTML,
			reply_markup=InlineKeyboardMarkup(
				[
					[InlineKeyboardButton(
						"See the full message",
						url=thread_url.replace("/raw","")
					)]
				]
			)
		)

		for f in files:
			await m.reply_document(f, file_name=f)
			os.remove(f)

	def listen_for_new_thread(self):
		# Schedule job every 5 seconds in interval
		self.job.add_job(self.__listening, trigger='interval', seconds=5)
