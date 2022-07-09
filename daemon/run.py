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
    host="localhost",
    user="root",
    database="lore_daemon"
)

db = Database(conn)

sched = AsyncIOScheduler()
sched.start()

job = Job(client=bot, job=sched, database=db)
job.listen_for_new_thread()

if __name__ == '__main__':
	bot.run()
	db.cur.close()
	db.conn.close()
