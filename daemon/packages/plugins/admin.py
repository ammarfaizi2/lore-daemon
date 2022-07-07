from pyrogram import Client, filters, enums
from pyrogram.types import Message
from textwrap import indent
import io, import_expression, contextlib, traceback

@Client.on_message(
	filters.command(['d','debug']) &
	filters.user(["nekoha", "kiizuah"])
)
async def execute_v2(c: Client, m: Message):
	sep = m.text.split('\n')
	body = m.text.replace(sep[0] + '\n','')

	env = {"bot": c}
	env.update(globals())

	stdout = io.StringIO()
	to_compile = f'async def func(_, m):\n{indent(body, "  ")}'

	try:
		import_expression.exec(to_compile, env)
	except Exception as e:
		text = f"```{e.__class__.__name__}: {e}"[0:4096]+"```"

	func = env["func"]

	try:
		with contextlib.redirect_stdout(stdout):
			await func(c, m)
	except Exception:
		value = stdout.getvalue()
		text = f"```{value}{traceback.format_exc()}"[0:4096]+"```"
	else:
		value = stdout.getvalue()
		text = f"```{value}"[0:4096]+"```"

	await c.send_message(m.chat.id, text, parse_mode=enums.ParseMode.MARKDOWN)
