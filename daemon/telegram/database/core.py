# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


from .methods import DBMethods


class DB(DBMethods):
	def __init__(self, conn):
		self.conn = conn
		self.conn.autocommit = True
		self.cur = self.conn.cursor(buffered=True)

	def ping(self, reconnect=True, attempts=3, delay=3):
		self.conn.ping(reconnect=reconnect, attempts=attempts,
				delay=delay)
		self.cur = self.conn.cursor(buffered=True)


	def __del__(self):
		self.cur.close()
		self.conn.close()
