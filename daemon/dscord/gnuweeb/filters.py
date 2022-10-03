# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

import discord
import asyncio
from typing import Any
from functools import wraps


def wait_on_limit(func):
	@wraps(func)
	async def callback(*args: Any) -> Any:
		while True:
			try:
				return await func(*args)
			except discord.errors.RateLimited as e:
				_flood_exceptions(e)
				print("[wait_on_limit]: Woken up from flood wait...")
	return callback


async def _flood_exceptions(e: "discord.errors.RateLimited"):
	wait = e.retry_after
	print(f"[wait_on_limit]: Sleeping for {wait} seconds due to Telegram limit")
	await asyncio.sleep(wait)
