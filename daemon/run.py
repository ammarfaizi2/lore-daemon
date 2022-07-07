from pyrogram import Client, idle
from packages import Job

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os

load_dotenv()

bot = Client(
	"EmailScrap",
	api_id=int(os.getenv("API_ID")),
	api_hash=os.getenv("API_HASH"),
	bot_token=os.getenv("BOT_TOKEN"),
	plugins=dict(
		root="packages.plugins"
	)
)

sched = AsyncIOScheduler()
sched.start()

job = Job(client=bot, job=sched)
# job.listen_for_new_thread()

if __name__ == '__main__':
	bot.run()
