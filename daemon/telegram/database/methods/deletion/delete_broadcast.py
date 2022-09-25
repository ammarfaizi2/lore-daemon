# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


class DeleteBroadcast:

	def delete_broadcast(self, chat_id: int):
		q = """
			DELETE FROM tg_broadcasts
			WHERE chat_id = %(chat_id)s
		"""
		self.cur.execute(q, {"chat_id": chat_id})
		return self.cur.rowcount > 0
