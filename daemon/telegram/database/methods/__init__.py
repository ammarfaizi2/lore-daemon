# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <kiizuha@gnuweeb.org>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#


from .deletion import Deletion
from .getter import Getter
from .insertion import Insertion


class DBMethods(
	Deletion,
	Getter,
	Insertion
): pass
