# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import os
import logging
import logging.config
from dotenv import load_dotenv
from mysql import connector
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dscord.gnuweeb import GWClient
from dscord.mailer import Listener
from dscord.mailer import Mutexes
from atom import Scraper


def main():
	load_dotenv("discord.env")

	sched = AsyncIOScheduler(
		job_defaults={
			"max_instances": 3,
			"misfire_grace_time": None
		}
	)

	logging.config.fileConfig("dscord/discord.logger.conf")
	logging.getLogger("apscheduler").setLevel(logging.WARNING)
	logging.getLogger("discord").setLevel(logging.WARNING)

	client = GWClient(
		db_conn=connector.connect(
			host=os.getenv("DB_HOST"),
			user=os.getenv("DB_USER"),
			port=int(os.environ.get("DB_PORT", 3306)),
			password=os.getenv("DB_PASS"),
			database=os.getenv("DB_NAME")
		)
	)

	mailer = Listener(
		client=client,
		sched=sched,
		scraper=Scraper(),
		mutexes=Mutexes()
	)

	client.mailer = mailer
	client.run(os.getenv("DISCORD_TOKEN"), log_handler=None)


if __name__ == "__main__":
	main()
