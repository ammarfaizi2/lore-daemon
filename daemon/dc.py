# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import os
from dotenv import load_dotenv
from mysql import connector

from dscord.gnuweeb import GWClient


def main():
	load_dotenv("discord.env")

	client = GWClient(
		db_conn=connector.connect(
			host=os.getenv("DB_HOST"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASS"),
			database=os.getenv("DB_NAME")
		)
	)
	client.run(os.getenv("DISCORD_TOKEN"), log_handler=None)


if __name__ == "__main__":
	main()
