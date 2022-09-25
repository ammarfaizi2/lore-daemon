# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from pyrogram.types import Message
from pyrogram import filters
from telegram.packages import DaemonClient
from atom import Scraper
from atom import utils
from telegram import config
import shutil
import re
import asyncio


#
# This allows user to invoke the following commands:
#    /lore https://lore.kernel.org/path/message_id/raw
#    !lore https://lore.kernel.org/path/message_id/raw
#    .lore https://lore.kernel.org/path/message_id/raw
#
LORE_CMD_URL_PATTERN = r"^(?:\/|\.|\!)lore\s+(https?:\/\/lore\.kernel\.org\/\S+)"
@DaemonClient.on_message(
	filters.regex(LORE_CMD_URL_PATTERN) &
	config.admin_only
)
async def scrap_email(c: DaemonClient, m: Message):
	p = re.search(LORE_CMD_URL_PATTERN, m.text)
	if not p:
		return

	url = p.group(1)
	if not url:
		return

	s = Scraper()
	mail = await s.get_email_from_url(url)
	text, files, is_patch = utils.create_template(mail)

	if is_patch:
		m = await c.send_patch_email(
			mail, m.chat.id, text, m.id, url
		)
	else:
		text = "#ml\n" + text
		m = await c.send_text_email(
			m.chat.id, text, m.id, url
		)

	for d, f in files:
		await m.reply_document(f"{d}/{f}", file_name=f)
		await asyncio.sleep(1)

	if files:
		shutil.rmtree(str(files[0][0]))
