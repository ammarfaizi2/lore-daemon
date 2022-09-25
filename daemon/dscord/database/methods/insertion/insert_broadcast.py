from mysql.connector import errors
from datetime import datetime


class InsertBroadcast:

	def save_broadcast(
		self,
		guild_id: int,
		channel_id: int,
		channel_name: str,
		channel_link: str = None,
	):
		try:
			return self.__insert_broadcast(
				guild_id=guild_id,
				channel_id=channel_id,
				channel_name=channel_name,
				channel_link=channel_link
			)
		except errors.IntegrityError:
			#
			# Duplicate data, skip!
			#
			return None


	def __insert_broadcast(
		self,
		guild_id: int,
		channel_id: int,
		channel_name: str,
		channel_link: str = None,
	):
		q = """
			INSERT INTO dc_broadcasts
			(guild_id, channel_id, channel_name, channel_link, created_at)
			VALUES (%s, %s, %s, %s, %s)
		"""
		values = (guild_id, channel_id, channel_name, channel_link, datetime.utcnow())
		self.cur.execute(q, values)
		return self.cur.lastrowid
