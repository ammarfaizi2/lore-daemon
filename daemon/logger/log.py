import logging
import os
from enums import Platform


class BotLogger(logging.Logger):

	def __init__(
		self,
		platform: Platform = Platform.TELEGRAM,
		level: int = logging.WARNING
	) -> None:

		self.platform = str(platform.value)
		self.level = level

		plat_rep = self.platform.replace("discord", "dscord")
		self.file_name = f"{plat_rep}/" \
			f"{os.getenv('STORAGE_DIR', 'storage')}/" \
			f"{self.platform}.log"

		self.file_fmt = "{" \
			"'time': '%(asctime)s'," \
			"'func': '%(name)s: %(funcName)s'," \
			"'path': '%(pathname)s'," \
			"'level': '%(levelname)s'," \
			"'msg': '%(message)s'"\
		"}"

		self.stream_fmt = "%(asctime)s | " \
			"%(name)s: %(funcName)s | " \
			"%(levelname)s | " \
			"%(message)s"


	def init(self):
		super().__init__(self.platform, self.level)

		file_handler = logging.FileHandler(self.file_name)
		stream_handler = logging.StreamHandler()

		file_fmtr = logging.Formatter(self.file_fmt)
		stream_fmtr = logging.Formatter(self.stream_fmt)

		file_handler.setFormatter(file_fmtr)
		stream_handler.setFormatter(stream_fmtr)

		file_handler.setLevel(logging.WARNING)
		self.setLevel(logging.INFO)

		self.addHandler(file_handler)
		self.addHandler(stream_handler)
