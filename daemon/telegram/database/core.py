# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from mysql import connector
from .methods import DBMethods


class DB(DBMethods):
	def __init__(self, host, user, password, database):
		self.host = host
		self.user = user
		self.password = password
		self.database = database
		self.conn = None
		self.connect()

	#
	# Allow the caller to reconnect.
	#
	def connect(self):
		if self.conn:
			self.close()

		self.conn = connector.connect(
			host=self.host,
			user=self.user,
			password=self.password,
			database=self.database
		)
		self.conn.autocommit = True
		self.cur = self.conn.cursor(buffered=True)

	def close(self):
		self.cur.close()
		self.conn.close()

	def __del__(self):
		self.close()
