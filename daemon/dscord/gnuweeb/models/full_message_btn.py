from discord import ui
from discord import ButtonStyle


class FullMessageBtn(ui.View):
	def __init__(self, url: str):
		super().__init__()
		self.add_item(ui.Button(
			label='See the full message',
			style=ButtonStyle.gray,
			url=url
		))
