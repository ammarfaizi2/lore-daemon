# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


from mysql.connector import errors
from datetime import datetime


class InsertEmail:

	def save_email(self, email_msg_id):
		try:
			return self.__insert_email(email_msg_id)
		except errors.IntegrityError:
			#
			# Duplicate data, skip!
			#
			return None


	def __insert_email(self, email_msg_id):
		q = "INSERT INTO tg_emails (message_id, created_at) VALUES (%s, %s)"
		self.cur.execute(q, (email_msg_id, datetime.utcnow()))
		return self.cur.lastrowid
