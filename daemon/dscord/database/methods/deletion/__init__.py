# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


from .delete_atom import DeleteAtom
from .delete_broadcast import DeleteBroadcast


class Deletion(
	DeleteAtom,
	DeleteBroadcast
): pass
