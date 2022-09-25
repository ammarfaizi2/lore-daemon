# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


class GetTelegramReply:

	def get_reply_id(self, email_msg_id, chat_id):
		'''
		Get Telegram message ID sent match with
                email message ID and Telegram chat ID.
                - Return Telegram message ID if exists: `int`
                - Return None if not exists`
		'''
		q = """
			SELECT tg_mail_msg.tg_msg_id
			FROM tg_emails INNER JOIN tg_mail_msg
			ON tg_emails.id = tg_mail_msg.email_id
			WHERE tg_emails.message_id = %(email_msg_id)s
			AND tg_mail_msg.chat_id = %(chat_id)s
		"""

		self.cur.execute(q, {
                        "email_msg_id": email_msg_id,
                        "chat_id": chat_id
                })
		res = self.cur.fetchone()
		if not bool(res):
			return None

		return res[0]
