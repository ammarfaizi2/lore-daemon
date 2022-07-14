# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram import Client
from packages import Job, Database

from mysql import connector
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os

load_dotenv()

bot = Client(
	"EmailScrap",
	api_id=int(os.getenv("API_ID")),
	api_hash=os.getenv("API_HASH"),
	bot_token=os.getenv("BOT_TOKEN"),
	plugins=dict(
		root="packages.plugins"
	)
)

conn = connector.connect(
	host=os.getenv("DB_HOST"),
	user=os.getenv("DB_USER"),
	password=os.getenv("DB_PASS"),
	database=os.getenv("DB_NAME")
)

db = Database(conn)

sched = AsyncIOScheduler(
	job_defaults={
		"max_instances": ,
		"misfire_grace_time": 15*60
	}
)
sched.start()

job = Job(client=bot, job=sched, database=db)
job.listen_for_new_thread()

if __name__ == '__main__':
	bot.run()
	db.cur.close()
	db.conn.close()
