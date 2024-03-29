# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from pyrogram.errors.exceptions.flood_420 import FloodWait
from typing import Any, Callable, TypeVar, Coroutine
from typing_extensions import ParamSpec, ParamSpecArgs, ParamSpecKwargs
from functools import wraps
import re
import asyncio
import logging


__all__ = ["handle_flood"]

log = logging.getLogger("telegram")
T = TypeVar("T")
P = ParamSpec("P")


def handle_flood(func: Callable[P, Coroutine[Any,Any,T]]) -> Callable[P, Coroutine[Any,Any,T]]:
	@wraps(func)
	async def callback(*args: ParamSpecArgs, **kwargs: ParamSpecKwargs) -> T:
		while True:
			try:
				return await func(*args, **kwargs)
			except FloodWait as e:
				_flood_exceptions(e)
				log.info("Woken up from flood wait...")
	return callback


async def _flood_exceptions(e):
	x = re.search(r"A wait of (\d+) seconds is required", str(e))
	if not x:
		raise e

	n = int(x.group(1))
	log.info(f"Sleeping for {n} seconds due to Telegram limit")
	await asyncio.sleep(n)
