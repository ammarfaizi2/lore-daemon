# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from mysql import connector
from pyrogram import idle
from atom import Scraper
from telegram.packages import DaemonTelegram
from telegram.mailer import BotMutexes
from telegram.mailer import Bot
from logger import BotLogger
import os


def main():
	load_dotenv("telegram.env")

	logger = BotLogger()
	logger.init()

	client = DaemonTelegram(
		"telegram/storage/EmailScraper",
		api_id=int(os.getenv("API_ID")),
		api_hash=os.getenv("API_HASH"),
		bot_token=os.getenv("BOT_TOKEN"),
		logger=logger,
		conn=connector.connect(
			host=os.getenv("DB_HOST"),
			user=os.getenv("DB_USER"),
			port=int(os.environ.get("DB_PORT", 3306)),
			password=os.getenv("DB_PASS"),
			database=os.getenv("DB_NAME")
		),
		plugins=dict(
			root="telegram.packages.plugins"
		),
	)

	sched = AsyncIOScheduler(
		job_defaults={
			"max_instances": 3,
			"misfire_grace_time": None
		}
	)

	bot = Bot(
		client=client,
		sched=sched,
		scraper=Scraper(),
		mutexes=BotMutexes()
	)
	bot.run()

if __name__ == '__main__':
	main()
