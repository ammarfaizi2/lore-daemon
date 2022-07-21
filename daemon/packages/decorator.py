# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram.errors.exceptions.flood_420 import FloodWait
from pyrogram.types import Message
from typing import Any, Callable, TypeVar
from functools import wraps
import re
import asyncio

__all__ = ["handle_flood"]

T = TypeVar("T", bound=Message)

#
# TODO(Muhammad Rizki): Add more typing for @handle_flood
#
def handle_flood(func: Callable[[T], T]) -> Callable[[T], T]:
	@wraps(func)
	async def callback(*args: Any) -> Any:
		while True:
			try:
				return await func(*args)
			except FloodWait as e:
				#
				# Aiee... we hit our limit.
				# Let's slow down a bit.
				#
				_flood_exceptions(e)
				print("[__handle_telegram_floodwait]: Woken up from flood wait...")
	return callback


async def _flood_exceptions(e):
	x = re.search(r"A wait of (\d+) seconds is required", str(e))
	if not x:
		raise e

	n = int(x.group(1))
	print(f"[____handle_telegram_floodwait]: Sleeping for {n} seconds due to Telegram limit")
	await asyncio.sleep(n)
