# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from discord.ext import commands
from discord import Interaction
from discord import app_commands

from atom import utils
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


	@atom.command(
		name="add",
		description="Add lore atom URL for receiving lore emails."
	)
	@app_commands.describe(url='Lore atom URL.')
	@filters.lore_admin
	async def add_atom(self, i: "Interaction", url: str):
		is_atom = await utils.is_atom_url(url)
		if not is_atom:
			t = "Invalid Atom URL."
			await i.response.send_message(t, ephemeral=True)
			return

		inserted = self.bot.db.save_atom(url)
		if inserted is None:
			t = f"This URL already listened for new email."
			await i.response.send_message(t, ephemeral=True)
			return

		t = f"Success add **{url}** for listening new email."
		await i.response.send_message(t, ephemeral=True)


	@atom.command(
		name="delete",
		description="Delete lore atom URL from receiving lore emails."
	)
	@app_commands.describe(url='Lore atom URL.')
	@filters.lore_admin
	async def del_atom(self, i: "Interaction", url: str):
		success = self.bot.db.delete_atom(url)
		if not success:
			t = "Failed to delete atom URL\n"
			t += "Maybe because already deleted or not exists."
			await i.response.send_message(t, ephemeral=True)
			return

		t = f"Success delete **{url}** from receiving lore emails."
		await i.response.send_message(t, ephemeral=True)
