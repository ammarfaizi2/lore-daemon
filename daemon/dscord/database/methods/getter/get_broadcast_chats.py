# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


class GetBroadcastChats:

	def get_broadcast_chats(self):
		'''
		Get broadcast chats that are currently
		listening for new email.
		- Return list of chat object: `List[Object]`
		'''
		q = """
			SELECT *
			FROM dc_broadcasts
		"""
		self.cur.execute(q)

		return self.cur.fetchall()
