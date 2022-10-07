# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


class GetAtomURL:

	def get_atom_urls(self):
		'''
		Get lore kernel raw email URLs.
		- Return list of raw email URLs: `List[str]`
		'''
		q = """
			SELECT dc_atoms.url
			FROM dc_atoms
		"""
		self.cur.execute(q)
		urls = self.cur.fetchall()

		return [u[0] for u in urls]
