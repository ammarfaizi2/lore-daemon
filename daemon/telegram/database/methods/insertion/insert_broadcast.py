# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


from mysql.connector import errors
from datetime import datetime


class InsertBroadcast:

	def save_broadcast(
		self,
		chat_id: int,
		name: str,
		type: str,
		created_at: "datetime",
		username: str = None,
		link: str = None,
	):
		try:
			return self.__insert_broadcast(
				chat_id=chat_id,
				name=name,
				type=type,
				created_at=created_at,
				username=username,
				link=link
			)
		except errors.IntegrityError:
			#
			# Duplicate data, skip!
			#
			return None


	def __insert_broadcast(
		self,
		chat_id: int,
		name: str,
		type: str,
		created_at: "datetime",
		username: str = None,
		link: str = None,
	):
		q = """
			INSERT INTO tg_broadcasts
			(chat_id, username, name, type, link, created_at)
			VALUES
			(%s, %s, %s, %s, %s, %s)
		"""
		values = (chat_id, username, name, type, link, created_at)
		self.cur.execute(q, values)
		return self.cur.lastrowid
