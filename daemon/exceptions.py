from typing import Optional

class DaemonException(Exception):
	thread_url: Optional[str] = None
	atom_url: Optional[str] = None
	original_exception: Optional[str] = None

	def __str__(self) -> str:
		return self.original_exception

	def set_atom_url(self, url: str):
		self.atom_url = url

	def set_thread_url(self, url: str):
		self.thread_url = url

	def set_message(self, msg: str):
		self.original_exception = msg
