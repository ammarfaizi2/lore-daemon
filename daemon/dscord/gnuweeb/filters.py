# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


import asyncio
from typing import Any, Callable, TypeVar, Coroutine
from typing_extensions import ParamSpec, ParamSpecArgs, ParamSpecKwargs
from functools import wraps

import discord
from discord import Interaction

from dscord import config
from logger import BotLogger


T = TypeVar("T")
P = ParamSpec("P")


def lore_admin(func: Callable[P, Coroutine[Any,Any,T]]) -> Callable[P, Coroutine[Any,Any,T]]:
	@wraps(func)
	async def callback(*args: ParamSpecArgs, **kwargs: ParamSpecKwargs) -> T:
		i: "Interaction" = args[1]
		user_roles = [role.id for role in i.user.roles]

		if config.ADMIN_ROLE_ID not in user_roles:
			return await i.response.send_message(
				"Sorry, you don't have this permission\n"\
				"Tell the server admin to add you lore admin role.",
				ephemeral=True
			)
		if config.ADMIN_ROLE_ID in user_roles:
			return await func(*args, **kwargs)

	return callback


def wait_on_limit(func: Callable[P, Coroutine[Any,Any,T]]) -> Callable[P, Coroutine[Any,Any,T]]:
	@wraps(func)
	async def callback(*args: ParamSpecArgs, **kwargs: ParamSpecKwargs) -> T:
		while True:
			try:
				return await func(*args, **kwargs)
			except discord.errors.RateLimited as e:
				# Calling logger attr from the GWClient() class
				logger = args[0].logger

				_flood_exceptions(e)
				logger.info("Woken up from flood wait...")
	return callback


async def _flood_exceptions(e: "discord.errors.RateLimited", logger: BotLogger):
	wait = e.retry_after
	logger.info(f"Sleeping for {wait} seconds due to Discord limit")
	await asyncio.sleep(wait)
