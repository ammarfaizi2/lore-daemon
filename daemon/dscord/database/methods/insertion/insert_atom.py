# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


from mysql.connector import errors
from datetime import datetime


class InsertAtom:

	def save_atom(self, atom: str):
		try:
			return self.__insert_atom(atom)
		except errors.IntegrityError:
			#
			# Duplicate data, skip!
			#
			return None


	def __insert_atom(self, atom: str):
		q = "INSERT INTO dc_atoms (url, created_at) VALUES (%s, %s)"
		self.cur.execute(q, (atom, datetime.utcnow()))
		return self.cur.lastrowid
