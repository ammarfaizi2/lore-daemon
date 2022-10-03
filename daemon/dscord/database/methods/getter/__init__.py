# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


from .get_atom_urls import GetAtomURL
from .get_broadcast_chats import GetBroadcastChats
from .get_email_id import GetEmailID


class Getter(
	GetAtomURL,
	GetBroadcastChats,
	GetEmailID
): pass
