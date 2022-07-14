# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from . import helper
from .structs import Emails
from scrapper import utils

from typing import Union, List, Dict
from datetime import datetime

class Database:
	def __init__(self, conn):
		self.conn = conn
		self.cur = self.conn.cursor()
		self.conn.autocommit = True

	def insert_email(self, msg_id: str):
		print(f"[insert_email]: {msg_id}")
		try:
			self.cur.execute(
				helper.SQL_EMAIL_INSERT,
				{
					"msg_id": msg_id,
					"date": datetime.utcnow()
				}
			)
		except:pass

		return self.cur.lastrowid

	def insert_telegram(
		self,
		email_id: int,
		chat_id: int,
		tg_msg_id: int
	):
		print(f"[insert_telegram]: {email_id},{chat_id}\n\n\n")
		self.cur.execute(
			helper.SQL_TG_INSERT,
			{
				"email_id": email_id,
				"chat_id": chat_id,
				"tg_msg_id": tg_msg_id,
				"date": datetime.utcnow()
			}
		)

	def get_email(
		self,
		msg_id: str
	) -> Union[None, "Emails"]:
		self.cur.execute(
			helper.SQL_CHECK_MSG_ID,
			{
				"msg_id": msg_id
			}
		)

		result = self.cur.fetchone()

		if not bool(result):
			return

		return Emails(
			result[0],
			result[1],
			result[2]
		)

	def reply_to(
		self,
		email_id: int
	) -> Union[None, int]:
		self.cur.execute(
			helper.SQL_REPLY_TO,
			{
				"msg_id": email_id
			}
		)

		result = self.cur.fetchone()

		if not bool(result):
			return

		return result[0]

	def get_emails(self):
		self.cur.execute(helper.SQL_GET_EMAILS)
		return self.cur.fetchall()

	def get_unread_threads(self, entries: List[Dict[str, str]]):
		new_entries = []

		for e in entries:
			thread_url = e['link']['@href']
			mail = self.get_email(
				utils.email_id_from_url(
					thread_url
				)
			)
			if not mail:
				new_entries.append(
					thread_url
					.replace("http:", "https:")
					+ "raw"
				)

		return new_entries

	#
	# Determine whether the email needs to be sent to @tg_chat_id.
	#
	# - Return an email id (PK) if it needs to be sent.
	# - Return None if it doesn't need to be sent.
	#
	def need_to_send_to_tg(self, email_msg_id, tg_chat_id):
		try:
			self.cur.execute("START TRANSACTION")
			self.cur.execute(
				helper.SQL_TRACK_EMAIL_BY_TG_CHAT_ID,
				{
					"email_msg_id": email_msg_id,
					"tg_chat_id": tg_chat_id
				}
			)
			res = self.cur.fetchone()

			if not bool(res):
				#
				# We don't have this email in database.
				# Save it!
				#
				email_id = self.insert_email(email_msg_id)
				if not email_id:
					#
					# Fail to insert? Something goes wrong!
					#
					email_id = None
					self.cur.execute("ROLLBACK")
					return None

			elif not bool(res[1]):
				#
				# If there is no Telegram chat message
				# record for this @email_msg_id, then
				# we return the @email_id and let the
				# caller send it to Telegram.
				#
				email_id = res[0]
			else:
				#
				# This email has already been sent to
				# @tg_chat_id.
				#
				# This informs the caller to skip sending
				# this email to @tg_chat_id.
				#
				email_id = None

			self.cur.execute("COMMIT")
			return email_id
		except:
			self.cur.execute("ROLLBACK")
			return None

	def get_tg_reply_to(email_msg_id, tg_chat_id):
		try:
			self.cur.execute("START TRANSACTION")
			self.cur.execute(
				helper.SQL_TRACK_EMAIL_BY_TG_CHAT_ID,
				{
					"email_msg_id": email_msg_id,
					"tg_chat_id": tg_chat_id
				}
			)
			res = self.cur.fetchone()

			if not bool(res):
				#
				# We don't have this email in database.
				# Save it!
				#
				email_id = self.insert_email(email_msg_id)
				if not email_id:
					#
					# Fail to insert? Something goes wrong!
					#
					email_id = None
					self.cur.execute("ROLLBACK")
					return None

			elif not bool(res[1]):
				#
				# If there is no Telegram chat message
				# record for this @email_msg_id, then
				# we return the @email_id and let the
				# caller send it to Telegram.
				#
				email_id = res[0]
			else:
				#
				# This email has already been sent to
				# @tg_chat_id.
				#
				# This informs the caller to skip sending
				# this email to @tg_chat_id.
				#
				email_id = None

			self.cur.execute("COMMIT")
			return email_id
		except:
			self.cur.execute("ROLLBACK")
			return None


	def get_tg_reply_to(self, email_id, tg_chat_id):
		self.cur.execute(
			helper.SQL_TG_REPLY_TO,
			{
				"email_id": email_id,
				"chat_id": tg_chat_id
			}
		)
		res = self.cur.fetchone()

		if not bool(res):
			return None

		return res[0]
