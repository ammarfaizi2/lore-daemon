# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from datetime import datetime
import mysql


class Db():
	def __init__(self, conn):
		self.conn = conn
		self.conn.autocommit = True
		self.cur = self.conn.cursor(buffered=True)


	def __del__(self):
		self.cur.close()
		self.conn.close()


	def save_email_msg_id(self, email_msg_id):
		try:
			return self.__save_email_msg_id(email_msg_id)
		except mysql.connector.errors.IntegrityError:
			#
			# Duplicate data, skip!
			#
			return None


	def __save_email_msg_id(self, email_msg_id):
		q = "INSERT INTO emails (message_id, created_at) VALUES (%s, %s)"
		self.cur.execute(q, (email_msg_id, datetime.utcnow()))
		return self.cur.lastrowid


	def insert_telegram(self, email_id, tg_chat_id, tg_msg_id):
		q = """
			INSERT INTO tg_emails
			(email_id, chat_id, tg_msg_id, created_at)
			VALUES (%s, %s, %s, %s);
		"""
		self.cur.execute(q, (email_id, tg_chat_id, tg_msg_id,
				 datetime.utcnow()))
		return self.cur.lastrowid


	#
	# Determine whether the email needs to be sent to @tg_chat_id.
	#
	# - Return an email id (PK) if it needs to be sent.
	# - Return None if it doesn't need to be sent.
	#
	def need_to_send_to_tg(self, email_msg_id, tg_chat_id):
		q = """
			SELECT emails.id, tg_emails.id FROM emails LEFT JOIN tg_emails
			ON emails.id = tg_emails.email_id
			WHERE emails.message_id = %(email_msg_id)s
			AND tg_emails.chat_id = %(tg_chat_id)s
			LIMIT 1
		"""

		self.cur.execute(
			q,
			{
				"email_msg_id": email_msg_id,
				"tg_chat_id": tg_chat_id
			}
		)
		res = self.cur.fetchone()
		if bool(res):
			#
			# This email has already been sent to
			# @tg_chat_id.
			#
			return None

		q = """
			SELECT id FROM emails WHERE message_id = %(email_msg_id)s
		"""
		self.cur.execute(q, {"email_msg_id": email_msg_id})
		res = self.cur.fetchone()
		if not bool(res):
			#
			# Something goes wrong, skip!
			#
			return None

		return int(res[0])


	def get_tg_reply_to(self, email_msg_id, tg_chat_id):
		q = """
			SELECT tg_emails.tg_msg_id
			FROM emails INNER JOIN tg_emails
			ON emails.id = tg_emails.email_id
			WHERE emails.message_id = %(email_msg_id)s
			AND tg_emails.chat_id = %(chat_id)s
		"""

		self.cur.execute(
			q,
			{
				"email_msg_id": email_msg_id,
				"chat_id": tg_chat_id
			}
		)
		res = self.cur.fetchone()
		if not bool(res):
			return None

		return res[0]


	def get_atom_urls(self):
		q = """
			SELECT atom_urls.url
			FROM atom_urls
		"""
		self.cur.execute(q)
		urls = self.cur.fetchall()

		return [u[0] for u in urls]


	def get_broadcast_chats(self):
		q = """
			SELECT *
			FROM broadcast_chats
		"""
		self.cur.execute(q)

		return self.cur.fetchall()
