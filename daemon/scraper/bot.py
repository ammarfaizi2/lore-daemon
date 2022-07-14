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
import xmltodict
import pyrogram
import asyncio
import shutil
import re


class BotMutexes():
	def __init__(self):
		self.send_to_tg = asyncio.Lock()


class Bot():
	ATOM_URLS = [
		# "https://lore.kernel.org/io-uring/new.atom",
		# "https://lore.kernel.org/linux-sgx/new.atom",
		"https://lore.kernel.org/netdev/new.atom"
	]

	TG_CHAT_IDS = [
		-1001394203410
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
		self.runner = self.sched.add_job(
			func=self.__run,
			misfire_grace_time=None,
			max_instances=1
		)


	async def __run(self):
		print("[__run]")
		for url in self.ATOM_URLS:
			await self.__handle_atom_url(url)

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
				await self.__send_to_tg(url, mail, tg_chat_id)
			await asyncio.sleep(1)


	# @__must_hold(self.mutexes.send_to_tg)
	async def __send_to_tg(self, url, mail, tg_chat_id):
		email_msg_id = utils.get_email_msg_id(mail)
		if not email_msg_id:
			#
			# Malformed email?
			#
			return

		self.db.save_email_msg_id(email_msg_id)
		text, files, is_patch = utils.create_template(mail)

		if is_patch:
			m = await self.__send_patch_msg(mail, tg_chat_id, text, url)
		else:
			m = await self.__send_text_msg(tg_chat_id, text, url)

		for d, f in files:
			await m.reply_document(f"{d}/{f}", file_name=f)
			await asyncio.sleep(1)

		if files:
			shutil.rmtree(str(files[0][0]))


	async def __send_patch_msg(self, mail, tg_chat_id, text, url):
		print("[__send_patch_msg]")
		tmp = utils.gen_temp(url)
		fnm = str(mail.get("subject"))
		sch = re.search(utils.PATCH_PATTERN, fnm, re.IGNORECASE)
		num = "%04d" % int(sch.group(1))
		fnm = slugify(sch.group(3))
		fnm = f"{tmp}/{num}-{fnm}.patch"
		cap = text.split("\n\n")[0]

		with open(fnm, "wb") as f:
			f.write(bytes(text, encoding="utf8"))

		caption = (
			"#patch #ml\n" +
			cap.rstrip()
				.replace("<", "&lt;")
				.replace(">","&gt;")
				.replace("�"," ")
		)

		ret = await self.__handle_telegram_floodwait(
			self.____send_patch_msg,
			*[tg_chat_id, fnm, caption, url]
		)
		shutil.rmtree(tmp)
		return ret


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


	async def ____handle_telegram_floodwait(self, e):
		x = str(e)
		x = re.search(r"A wait of (\d+) seconds is required", x)
		if not x:
			raise e

		n = int(x.group(1))
		print("[____handle_telegram_floodwait]: Sleeping for %d seconds due to Telegram limit" % (n))
		await asyncio.sleep(n)


	async def ____send_patch_msg(self, tg_chat_id, fnm, caption, url):
		return await self.client.send_document(
			tg_chat_id,
			fnm,
			caption=caption,
			reply_to_message_id=None,
			parse_mode=enums.ParseMode.HTML,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)


	async def ____send_text_msg(self, tg_chat_id, text, url):
		print("[__send_text_msg]")
		return await self.client.send_message(
			tg_chat_id,
			text,
			reply_to_message_id=None,
			parse_mode=enums.ParseMode.HTML,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)
