# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

import asyncio
import traceback
import re
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import File
from discord import Message

from dscord.gnuweeb import GWClient
from atom.scraper import Scraper
from atom import utils
from enums import Platform


class Mutexes:
	def __init__(self):
		self.lock = asyncio.Lock()


class Listener:
	def __init__(
                self,
                client: "GWClient",
                sched: "AsyncIOScheduler",
		scraper: "Scraper",
                mutexes: "Mutexes"
        ):
		self.client = client
		self.sched = sched
		self.scraper = scraper
		self.mutexes = mutexes
		self.db = client.db
		self.isRunnerFixed = False
		self.runner = None


	def run(self):
		#
		# Execute __run() once to avoid high latency at
		# initilization.
		#
		print("Initialize listener...\n")
		self.sched.start()
		self.runner = self.sched.add_job(func=self.__run)


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
			async with self.mutexes.lock:
				should_wait = \
				await self.__send_to_discord(url, mail,
							chat[1], chat[2])

			if should_wait:
				await asyncio.sleep(1)


	# @__must_hold(self.mutexes.lock)
	async def __send_to_discord(self, url, mail, dc_guild_id, dc_chat_id):
		email_msg_id = utils.get_email_msg_id(mail)
		if not email_msg_id:
			#
			# It doesn't have a Message-Id.
			# A malformed email. Skip!
			#
			return False

		email_id = self.__get_email_id_sent(
			email_msg_id=email_msg_id,
			dc_chat_id=dc_chat_id
		)
		if not email_id:
			#
			# Email has already been sent to Discord.
			# Skip!
			#
			return False

		text, files, is_patch = utils.create_template(mail, Platform.DISCORD)
		reply_to = self.get_discord_reply(mail, dc_chat_id)
		url = str(re.sub(r"/raw$", "", url))

		if is_patch:
			m: Message = await self.client.send_patch_email(
				mail, dc_guild_id, dc_chat_id, text, reply_to, url
			)
		else:
			text = "#ml\n" + text
			m: Message = await self.client.send_text_email(
				dc_guild_id, dc_chat_id, text, reply_to, url
			)

		self.db.save_discord_mail(email_id, m.channel.id, m.id)

		for d, f in files:
			await m.reply(file=File(f"{d}/{f}"))
			await asyncio.sleep(1)

		utils.remove_patch(files)

		return True


	def __get_email_id_sent(self, email_msg_id, dc_chat_id):
		email_id = self.db.save_email(email_msg_id)
		if email_id:
			return email_id

		email_id = self.db.get_email_id(email_msg_id, dc_chat_id)
		return email_id


	def get_discord_reply(self, mail, dc_chat_id):
		reply_to = mail.get("in-reply-to")
		if not reply_to:
			return None

		reply_to = utils.extract_email_msg_id(reply_to)
		if not reply_to:
			return None

		return self.db.get_reply_id(reply_to, dc_chat_id)
