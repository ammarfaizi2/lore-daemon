# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from .manage_atom import ManageAtomSC
from .manage_broadcast import ManageBroadcastSC
from .get_lore_mail import GetLoreSC


class SlashCommands(
	GetLoreSC,
	ManageAtomSC,
	ManageBroadcastSC
): pass
