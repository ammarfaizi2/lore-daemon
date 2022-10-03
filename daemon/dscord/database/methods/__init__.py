# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


from .insertion import Insertion
from .getter import Getter


class DBMethods(
	Insertion,
	Getter
): pass
