# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
#


from .insertion import Insertion
from .getter import Getter
from .deletion import Deletion


class DBMethods(
	Insertion,
	Getter,
	Deletion
): pass
