# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


class DeleteAtom:

	def delete_atom(self, atom: str):
		q = """
			DELETE FROM dc_atoms
			WHERE url = %(atom)s
		"""
		self.cur.execute(q, {"atom": atom})
		return self.cur.rowcount > 0
