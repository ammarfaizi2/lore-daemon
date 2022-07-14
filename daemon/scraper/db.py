# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from datetime import datetime
import mysql

class Db():
	def __init__(self, conn):
		self.conn = conn
		self.conn.autocommit = False
		self.cur = self.conn.cursor()


	def __del__(self):
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
		self.conn.commit()
		return self.cur.lastrowid
