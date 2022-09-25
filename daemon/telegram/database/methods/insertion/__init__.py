# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from .insert_atom import InsertAtom
from .insert_broadcast import InsertBroadcast
from .insert_email import InsertEmail
from .insert_telegram import InsertTelegram


class Insertion(
	InsertAtom,
	InsertBroadcast,
	InsertEmail,
	InsertTelegram
): pass
