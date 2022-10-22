import enum
from .base import EnumBase


class Platform(EnumBase):
	DISCORD = enum.auto()
	TELEGRAM = enum.auto()
