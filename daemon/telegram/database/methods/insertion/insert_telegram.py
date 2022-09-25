# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


from datetime import datetime


class InsertTelegram:

	def save_telegram_mail(self, email_id, tg_chat_id, tg_msg_id):
		q = """
			INSERT INTO tg_mail_msg
			(email_id, chat_id, tg_msg_id, created_at)
			VALUES (%s, %s, %s, %s);
		"""
		self.cur.execute(q, (email_id, tg_chat_id, tg_msg_id,
				datetime.utcnow()))
		return self.cur.lastrowid
