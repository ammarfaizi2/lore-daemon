from datetime import datetime


class InsertDiscord:

	def save_discord_mail(self, email_id, channel_id, dc_msg_id):
		q = """
			INSERT INTO dc_mail_msg
			(email_id, channel_id, dc_msg_id, created_at)
			VALUES (%s, %s, %s, %s);
		"""
		self.cur.execute(q, (email_id, channel_id, dc_msg_id,
				datetime.utcnow()))
		return self.cur.lastrowid
