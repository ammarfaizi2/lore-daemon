# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from email.message import Message
from scraper import BotMutexes
from pyrogram import Client
from scraper import Scraper
from scraper import Bot
from mysql import connector
from dotenv import load_dotenv
import asyncio
import os
import re

load_dotenv()

client = Client(
	"EmailScraper",
	api_id=int(os.getenv("API_ID")),
	api_hash=os.getenv("API_HASH"),
	bot_token=os.getenv("BOT_TOKEN")
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
	mutexes=BotMutexes(),
	conn=connector.connect(
		host=os.getenv("DB_HOST"),
		user=os.getenv("DB_USER"),
		password=os.getenv("DB_PASS"),
		database=os.getenv("DB_NAME")
	)
)
sched.start()
bot.run()
client.run()
