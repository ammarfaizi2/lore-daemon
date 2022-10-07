# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


class GetDiscordReply:

	def get_reply_id(self, email_id, channel_id):
		'''
		Get Telegram message ID sent match with
		email message ID and Telegram chat ID.
		- Return Telegram message ID if exists: `int`
		- Return None if not exists`
		'''
		q = """
			SELECT dc_mail_msg.dc_msg_id
			FROM dc_emails INNER JOIN dc_mail_msg
			ON dc_emails.id = dc_mail_msg.email_id
			WHERE dc_emails.message_id = %(email_msg_id)s
			AND dc_mail_msg.channel_id = %(channel_id)s
		"""

		self.cur.execute(q, {
			"email_msg_id": email_id,
			"channel_id": channel_id
		})
		res = self.cur.fetchone()
		if not bool(res):
			return None

		return res[0]
