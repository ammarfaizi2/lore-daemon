# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import InlineKeyboardButton
from slugify import slugify
from pyrogram import Client
from scraper import Scraper
from pyrogram import enums
from . import utils
from .db import Db
import pyrogram
import asyncio
import shutil
import re


class BotMutexes():
	def __init__(self):
		self.send_to_tg = asyncio.Lock()


class Bot():
	ATOM_URLS = [
		"https://lore.kernel.org/io-uring/new.atom",
		"https://lore.kernel.org/linux-sgx/new.atom",
	]

	TG_CHAT_IDS = [
		-1001394203410,
		-1001673279485,
	]


	def __init__(self, client: Client, sched: AsyncIOScheduler,
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
		for url in self.ATOM_URLS:
			try:
				await self.__handle_atom_url(url)
			except Exception as e:
				print(f"[__run]: Error: {e}")

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
		for tg_chat_id in self.TG_CHAT_IDS:
			async with self.mutexes.send_to_tg:
				should_wait = await self.__send_to_tg(url, mail,
								      tg_chat_id)

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
			m = await self.__send_patch_msg(mail, tg_chat_id,
							reply_to, text, url)
		else:
			text = "#ml\n" + text
			m = await self.__send_text_msg(tg_chat_id, reply_to,
						       text, url)

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


	async def __send_patch_msg(self, mail, tg_chat_id, reply_to, text, url):
		print("[__send_patch_msg]")
		
		tmp, fnm, caption, url = Bot.prepare_send_patch(mail, text, url)
		ret = await self.__handle_telegram_floodwait(
			self.____send_patch_msg,
			*[tg_chat_id, reply_to, fnm, caption, url]
		)
		Bot.clean_up_after_send_patch(tmp)
		return ret


	@staticmethod
	def prepare_send_patch(mail, text, url):
		tmp = utils.gen_temp(url)
		fnm = str(mail.get("subject"))
		sch = re.search(utils.PATCH_PATTERN, fnm, re.IGNORECASE)

		nr_patch = sch.group(1)
		if not nr_patch:
			nr_patch = 1
		else:
			nr_patch = int(nr_patch)

		num = "%04d" % nr_patch
		fnm = slugify(sch.group(3)).replace("_", "-")
		file = f"{tmp}/{num}-{fnm}.patch"
		cap = text.split("\n\n")[0]

		with open(file, "wb") as f:
			f.write(bytes(text, encoding="utf8"))

		caption = (
			"#patch #ml\n" +
			cap.rstrip()
				.replace("<", "&lt;")
				.replace(">","&gt;")
				.replace("�"," ")
		)
		return tmp, file, caption, url


	@staticmethod
	def clean_up_after_send_patch(tmp):
		shutil.rmtree(tmp)


	async def __send_text_msg(self, *args):
		return await self.__handle_telegram_floodwait(
			self.____send_text_msg,
			*args
		)


	async def __handle_telegram_floodwait(self, callback, *args):
		while True:
			try:
				return await callback(*args)
			except pyrogram.errors.exceptions.flood_420.FloodWait as e:
				#
				# Aiee... we hit our limit.
				# Let's slow down a bit.
				#
				await self.____handle_telegram_floodwait(e)
				print("[__handle_telegram_floodwait]: Woken up from flood wait...")


	async def ____handle_telegram_floodwait(self, e):
		x = str(e)
		x = re.search(r"A wait of (\d+) seconds is required", x)
		if not x:
			raise e

		n = int(x.group(1))
		print(f"[____handle_telegram_floodwait]: Sleeping for {n} seconds due to Telegram limit")
		await asyncio.sleep(n)


	async def ____send_patch_msg(self, tg_chat_id, reply_to, fnm, caption,
				     url):
		return await self.client.send_document(
			tg_chat_id,
			fnm,
			caption=caption,
			reply_to_message_id=reply_to,
			parse_mode=enums.ParseMode.HTML,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)


	async def ____send_text_msg(self, tg_chat_id, reply_to, text, url):
		print("[__send_text_msg]")
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
