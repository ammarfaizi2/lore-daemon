# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#

from .on_ready import OnReady
from .on_error import OnError


class Events(
	OnReady,
	OnError
): pass
