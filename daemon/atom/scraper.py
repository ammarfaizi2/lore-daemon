# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from typing import Dict, List
import email.policy
import xmltodict
import httpx
import email


class Scraper():
	async def get_new_threads_urls(self, atom_url):
		ret = await self.__get_atom_content(atom_url)
		return await self.__get_new_threads_from_atom(ret)


	async def __get_atom_content(self, atom_url):
		async with httpx.AsyncClient() as client:
			res = await client.get(atom_url)
			if res.status_code == 200:
				return res.text
			raise Exception(f"[get_atom_content]: Returned {res.status_code} HTTP code")


	async def __get_new_threads_from_atom(self, atom):
		j: Dict[str, List[
			Dict[str, str]
		]] = xmltodict.parse(atom)["feed"]

		entry = []
		e = j["entry"]
		for i in e:
			entry.append({
				"link": i["link"]["@href"],
				"title": i["title"],
				"updated": i["updated"],
			})
		#
		# TODO(ammarfaizi2): Sort by title as well if the @updated is
		#                    identic.
		#
		entry.sort(key=lambda x: x["updated"])

		ret = []
		for i in entry:
			link = i["link"].replace("http://", "https://")
			ret.append(link + "raw")

		return ret


	async def get_email_from_url(self, url):
		async with httpx.AsyncClient() as client:
			res = await client.get(url)
			if res.status_code == 200:
				return email.message_from_string(
					res.text,
					policy=email.policy.default
				)
			raise Exception(f"[get_atom_content]: Returned {res.status_code} HTTP code")
