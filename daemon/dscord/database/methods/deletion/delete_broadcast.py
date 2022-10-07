# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


class DeleteBroadcast:

	def delete_broadcast(self, channel_id: int):
		q = """
			DELETE FROM dc_broadcasts
			WHERE channel_id = %(channel_id)s
		"""
		self.cur.execute(q, {"channel_id": channel_id})
		return self.cur.rowcount > 0
