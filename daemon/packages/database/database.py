# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from . import helper
from .structs import Emails, TGEmails

from typing import Union
from datetime import datetime

class Database:
	def __init__(self, conn):
		self.conn = conn
		self.cur = self.conn.cursor()
		self.conn.autocommit = True

	def insert_email(self, msg_id: str):
		if self.get_email(msg_id):
			return

		self.cur.execute(
			helper.SQL_EMAIL_INSERT,
			{
				"msg_id": msg_id,
				"date": datetime.utcnow()
			}
		)

		return self.cur.lastrowid

	def insert_telegram(
		self,
		email_id: int,
		chat_id: int,
		tg_msg_id: int
	):
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

	def reply_to(self, email_id: int):
		self.cur.execute(
			helper.SQL_REPLY_TO,
			{
				"email_id": email_id
			}
		)

		result = self.cur.fetchone()

		if not bool(result):
			return

		return TGEmails(
			result[0],
			result[1],
			result[2],
			result[3],
			result[4]
		)

	def get_emails(self):
		self.cur.execute(helper.SQL_GET_EMAILS)
		return self.cur.fetchall()
