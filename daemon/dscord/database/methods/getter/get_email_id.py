# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


class GetEmailID:

	def get_email_id(self, email_id, chat_id):
		'''
		Determine whether the email needs to be sent to @tg_chat_id.
		 - Return an email id (PK) if it needs to be sent
		 - Return None if it doesn't need to be sent
		'''
		if self.__is_sent(email_id, chat_id):
			return

		res = self.__email_id(email_id)
		if not bool(res):
			return

		return int(res[0])


	def __is_sent(self, email_id, channel_id):
		'''
		Checking if this email has already been sent
		or not.
		 - Return True if it's already been sent
		'''
		q = """
			SELECT dc_emails.id, dc_mail_msg.id FROM dc_emails
			LEFT JOIN dc_mail_msg
			ON dc_emails.id = dc_mail_msg.email_id
			WHERE dc_emails.message_id = %(email_msg_id)s
			AND dc_mail_msg.channel_id = %(channel_id)s
			LIMIT 1
		"""

		self.cur.execute(q, {
			"email_msg_id": email_id,
			"channel_id": channel_id
		})
		res = self.cur.fetchone()
		return bool(res)


	def __email_id(self, email_id):
		'''
		Get the email id if match with the email message_id.
		 - Return the result if it's match and exists
		'''
		q = """
			SELECT id FROM dc_emails WHERE message_id = %(email_id)s
		"""

		self.cur.execute(q, {"email_id": email_id})
		res = self.cur.fetchone()
		return res
