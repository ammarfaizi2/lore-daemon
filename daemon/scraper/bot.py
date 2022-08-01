# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from packages import DaemonClient
from scraper import Scraper
from . import utils
from .db import Db
import asyncio
import shutil
import re
import traceback


class BotMutexes():
	def __init__(self):
		self.send_to_tg = asyncio.Lock()


class Bot():
	def __init__(self, client: DaemonClient, sched: AsyncIOScheduler,
			scraper: Scraper, mutexes: BotMutexes, conn):
		self.client = client
		self.sched = sched
		self.scraper = scraper
		self.mutexes = mutexes
		self.db = Db(conn)
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
				should_wait = await self.__send_to_tg(url, mail,
									chat[1])

			if should_wait:
				await asyncio.sleep(1)


	# @__must_hold(self.mutexes.send_to_tg)
	async def __send_to_tg(self, url, mail, tg_chat_id):
		email_msg_id = utils.get_email_msg_id(mail)
		if not email_msg_id:
			#
			# It doesn't have a Message-Id.
			# A malformed email. Skip!
			#
			return False

		email_id = self.__need_to_send_to_telegram(email_msg_id,
							tg_chat_id)
		if not email_id:
			#
			# Email has already been sent to Telegram.
			# Skip!
			#
			return False

		text, files, is_patch = utils.create_template(mail)
		reply_to = self.get_tg_reply_to(mail, tg_chat_id)
		url = str(re.sub(r"/raw$", "", url))

		if is_patch:
			m = await self.client.send_patch_email(
				mail, tg_chat_id, text, reply_to, url
			)
		else:
			text = "#ml\n" + text
			m = await self.client.send_text_email(
				tg_chat_id, text,reply_to, url
			)

		self.db.insert_telegram(email_id, m.chat.id, m.id)
		for d, f in files:
			await m.reply_document(f"{d}/{f}", file_name=f)
			await asyncio.sleep(1)

		if files:
			shutil.rmtree(str(files[0][0]))

		return True


	def __need_to_send_to_telegram(self, email_msg_id, tg_chat_id):
		email_id = self.db.save_email_msg_id(email_msg_id)
		if email_id:
			return email_id

		email_id = self.db.need_to_send_to_tg(email_msg_id, tg_chat_id)
		return email_id


	def get_tg_reply_to(self, mail, tg_chat_id):
		reply_to = mail.get("in-reply-to")
		if not reply_to:
			return None

		reply_to = utils.extract_email_msg_id(reply_to)
		if not reply_to:
			return None

		return self.db.get_tg_reply_to(reply_to, tg_chat_id)
