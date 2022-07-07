from bs4 import BeautifulSoup

import httpx
import email.header
import email.policy
import email

class Scrapper:
	def __init__(self, url = None):
		self.url = url
		self.BASE_URL = "https://lore.kernel.org/io-uring/"
		self.thread_url = None

	async def get_new_thread(self):
		async with httpx.AsyncClient() as client:
			res = await client.get(self.BASE_URL)

			if res.status_code != 200:
				raise Exception(f"[get_new_thread]: URL Scrap return {res.status_code} status code")

			s = BeautifulSoup(res.text, 'lxml')
			pre = [a for a in s.find("body")][1]
			email = pre.find_next("a").get("href").replace("/T/#t", "/raw")
			return self.BASE_URL + email

	async def see_new_thread(self):
		if not bool(self.url):
			self.url = await self.get_new_thread()

		async with httpx.AsyncClient() as client:
			res = await client.get(self.url)

			if res.status_code != 200:
				raise Exception(f"[see_new_thread]: URL Scrap return {res.status_code} status code")

			content = res.text
			mail = email.message_from_string(content, policy=email.policy.default)
			return mail, self.url
