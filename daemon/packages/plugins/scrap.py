# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from scrapper import Scrapper, utils
from packages import constants
import os

@Client.on_message(
	filters.regex(constants.URL_REGEX) &
	filters.chat(["kiizuah", "nekoha", -1001673279485])
)
async def scrap_email(_, m: Message):
	s = Scrapper(m.text)
	thread, thread_url = await s.see_new_thread()

	template, files = utils.create_template(thread)

	m = await m.reply(
		template,
		parse_mode=enums.ParseMode.HTML,
		reply_markup=InlineKeyboardMarkup(
			[
				[InlineKeyboardButton(
					"See the full message",
					url=thread_url.replace("/raw","")
				)]
			]
		)
	)

	for f in files:
		await m.reply_document(f, file_name=f)
		os.remove(f)
