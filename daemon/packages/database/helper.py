# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

SQL_EMAIL_INSERT = """
	INSERT INTO emails (
		message_id,
		created_at
	) VALUES (
		%(msg_id)s,
		%(date)s
	)
"""

SQL_TG_INSERT = """
	INSERT INTO tg_emails (
		email_id,
		chat_id,
		tg_msg_id,
		created_at
	) VALUES (
		%(email_id)s,
		%(chat_id)s,
		%(tg_msg_id)s,
		%(date)s
	)
"""

SQL_CHECK_MSG_ID = """
	SELECT * FROM emails
	WHERE message_id = %(msg_id)s
"""

SQL_REPLY_TO = """
	SELECT * FROM tg_emails
	WHERE email_id = %(email_id)s
"""

SQL_GET_EMAILS = """
	SELECT * FROM emails
"""
