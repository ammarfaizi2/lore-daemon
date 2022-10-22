import enum


class EnumBase(enum.Enum):
	def _generate_next_value_(self, *args):
		return self.lower()

	def __repr__(self):
		return f"enums.{self}"
