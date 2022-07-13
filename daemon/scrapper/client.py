# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from . import utils

from typing import Dict, List
import xmltodict
import httpx
import email.policy
import email

class Scrapper:
	def __init__(self, url = None, database = None):
		self.url = url
		self.BASE_URL = "https://lore.kernel.org/io-uring/"
		self.thread_url = None
		self.db = database

	async def get_new_thread(self):
		async with httpx.AsyncClient() as client:
			res = await client.get(self.BASE_URL + "new.atom")

			if res.status_code != 200:
				raise Exception(f"[get_new_thread]: URL Scrap return {res.status_code} status code")

			json: Dict[str, List[
				Dict[str, str]
			]] = xmltodict.parse(res.text)['feed']

			entry = json['entry']
			entry.sort(key=lambda x: x["updated"])

			return self.db.get_unread_threads(entry)

	async def see_new_thread(self):
		urls = [self.url]

		if not self.url:
			urls = await self.get_new_thread()

		async with httpx.AsyncClient() as client:

			mails = []
			for u in urls:
				msg_id = utils.email_id_from_url(u)
				res = await client.get(u)

				if res.status_code != 200:
					raise Exception(f"[see_new_thread]: URL Scrap return {res.status_code} status code")

				mail = email.message_from_string(
					res.text,
					policy=email.policy.default
				)
				mails.append((mail, u, msg_id))

			return mails
