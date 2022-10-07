# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


from discord.ext import commands

from .events import Events
from .basic_commands import BasicCommands
from .slash_commands import SlashCommands


class Plugins(
	BasicCommands,
	Events,
	SlashCommands
): pass


async def setup(bot: "commands.Bot"):
	await bot.add_cog(Plugins(bot))
