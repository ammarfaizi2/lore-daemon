# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


from .insert_atom import InsertAtom
from .insert_broadcast import InsertBroadcast
from .insert_discord import InsertDiscord
from .insert_email import InsertEmail


class Insertion(
	InsertAtom,
	InsertBroadcast,
	InsertDiscord,
	InsertEmail
): pass
