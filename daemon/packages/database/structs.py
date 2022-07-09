# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from datetime import datetime
from dataclasses import dataclass

@dataclass
class Emails:
	id: int
	message_id: str
	created_at: datetime

@dataclass
class TGEmails:
	id: int
	email_id: int
	chat_id: int
	tg_msg_id: int
	created_at: datetime
