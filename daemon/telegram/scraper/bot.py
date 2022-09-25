# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from pyrogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.packages import DaemonClient
from telegram.scraper import Scraper
from . import utils
import asyncio
import shutil
import re
import traceback


class BotMutexes():
	def __init__(self):
		self.send_to_tg = asyncio.Lock()


class Bot():
	def __init__(self, client: DaemonClient, sched: AsyncIOScheduler,
			scraper: Scraper, mutexes: BotMutexes):
		self.client = client
		self.sched = sched
		self.scraper = scraper
		self.mutexes = mutexes
		self.db = client.db
		self.isRunnerFixed = False


	def run(self):
		#
		# Execute __run() once to avoid high latency at
		# initilization.
		#
		self.runner = self.sched.add_job(
			func=self.__run,
			misfire_grace_time=None,
			max_instances=1
		)


	async def __run(self):
		print("[__run]: Running...")
		for url in self.db.get_atom_urls():
			try:
				await self.__handle_atom_url(url)
			except:
				print(traceback.format_exc())

		if not self.isRunnerFixed:
			self.isRunnerFixed = True
			self.runner = self.sched.add_job(
				func=self.__run,
				trigger="interval",
				seconds=30,
				misfire_grace_time=None,
				max_instances=1
			)


	async def __handle_atom_url(self, url):
		urls = await self.scraper.get_new_threads_urls(url)
		for url in urls:
			mail = await self.scraper.get_email_from_url(url)
			await self.__handle_mail(url, mail)


	async def __handle_mail(self, url, mail):
		chats = self.db.get_broadcast_chats()
		for chat in chats:
			async with self.mutexes.send_to_tg:
				should_wait = await self.__send_mail(url, mail,
									chat[1])

			if should_wait:
				await asyncio.sleep(1)


	# @__must_hold(self.mutexes.send_to_tg)
	async def __send_mail(self, url, mail, tg_chat_id):
		email_msg_id = utils.get_email_msg_id(mail)
		if not email_msg_id:
			#
			# It doesn't have a Message-Id.
			# A malformed email. Skip!
			#
			return False

		email_id = self.__mail_id_from_db(email_msg_id,
							tg_chat_id)
		if not email_id:
			#
			# Email has already been sent to Telegram.
			# Skip!
			#
			return False

		text, files, is_patch = utils.create_template(mail)
		reply_to = self.get_reply(mail, tg_chat_id)
		url = str(re.sub(r"/raw$", "", url))

		if is_patch:
			m: "Message" = await self.client.send_patch_email(
				mail, tg_chat_id, text, reply_to, url
			)
		else:
			text = "#ml\n" + text
			m: "Message" = await self.client.send_text_email(
				tg_chat_id, text,reply_to, url
			)

		self.db.save_telegram_mail(email_id, m.chat.id, m.id)
		for d, f in files:
			await m.reply_document(f"{d}/{f}", file_name=f)
			await asyncio.sleep(1)

		if files:
			shutil.rmtree(str(files[0][0]))

		return True


	def __mail_id_from_db(self, email_msg_id, tg_chat_id):
		email_id = self.db.save_email(email_msg_id)
		if email_id:
			return email_id

		email_id = self.db.get_email_id(email_msg_id, tg_chat_id)
		return email_id


	def get_reply(self, mail, tg_chat_id):
		reply_to = mail.get("in-reply-to")
		if not reply_to:
			return None

		reply_to = utils.extract_email_msg_id(reply_to)
		if not reply_to:
			return None

		return self.db.get_reply_id(reply_to, tg_chat_id)
