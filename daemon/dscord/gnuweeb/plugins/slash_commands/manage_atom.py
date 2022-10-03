# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands
from discord import Interaction
from discord import app_commands

from dscord.gnuweeb import filters


class ManageAtomSC(commands.Cog):
	atom = app_commands.Group(
		name="atom",
		description="Manage lore atom URL."
	)

	def __init__(self, bot) -> None:
		self.bot = bot


	@atom.command(
		name="list",
		description="List of lore atom URL."
	)
	@filters.lore_admin
	async def list_atom(self, i: "Interaction"):
		atoms = self.bot.db.get_atom_urls()
		if len(atoms) == 0:
			t = "Currently empty."
			await i.response.send_message(t, ephemeral=True)
			return

		text = "List of atom URL that currently listened:\n"
		for u,n in zip(atoms, range(1, len(atoms)+1)):
			text += f"{n}. {u}\n"

		await i.response.send_message(text, ephemeral=True)
