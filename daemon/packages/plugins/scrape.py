# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import InlineKeyboardButton
from pyrogram.types import Message
from pyrogram import filters
from pyrogram import Client
from scraper import Scraper
from pyrogram import enums
from scraper import utils
from scraper import Bot
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
@Client.on_message(
	filters.regex(LORE_CMD_URL_PATTERN) &
	filters.chat(["kiizuah", "nekoha", -1001673279485])
)
async def scrap_email(_, m: Message):
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
		m = await __send_patch_msg(m, mail, text, url)
	else:
		text = "#ml\n" + text
		m = await __send_text_msg(m, text, url)

	for d, f in files:
		await m.reply_document(f"{d}/{f}", file_name=f)
		await asyncio.sleep(1)

	if files:
		shutil.rmtree(str(files[0][0]))


async def __send_patch_msg(m, mail, text, url):
	tmp, fnm, caption, url = Bot.prepare_send_patch(mail, text, url)
	ret = await m.reply_document(
		fnm,
		caption=caption,
		parse_mode=enums.ParseMode.HTML,
		reply_markup=InlineKeyboardMarkup([
			[InlineKeyboardButton(
				"See the full message",
				url=url
			)]
		])
	)
	Bot.clean_up_after_send_patch(tmp)
	return ret


async def __send_text_msg(m, text, url):
	return await m.reply(
		text,
		parse_mode=enums.ParseMode.HTML,
		reply_markup=InlineKeyboardMarkup([
			[InlineKeyboardButton(
				"See the full message",
				url=url.replace("/raw","")
			)]
		])
	)
