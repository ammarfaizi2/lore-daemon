# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import os
from dotenv import load_dotenv

from dscord.gnuweeb import GWClient


def main():
	load_dotenv("discord.env")

	client = GWClient()
	client.run(os.getenv("DISCORD_TOKEN"), log_handler=None)


if __name__ == "__main__":
	main()
