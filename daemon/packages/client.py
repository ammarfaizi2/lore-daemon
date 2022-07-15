from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union, BinaryIO


class DaemonClient(Client):
        def __init__(self, name: str, api_id: int,
                     api_hash: str, **kwargs):
                super().__init__(name, api_id,
                                api_hash, **kwargs)


        async def send_text_email(
                self,
                chat_id: Union[int, str],
                text: str,
                reply_to: int,
                url: str = None,
                parse_mode: ParseMode = ParseMode.HTML
        ) -> Message:
                print("[send_text_email]")
                return await self.send_message(
			chat_id=chat_id,
			text=text,
			reply_to_message_id=reply_to,
			parse_mode=parse_mode,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)


        async def send_patch_email(
                self,
                chat_id: Union[int, str],
                doc: Union[str, BinaryIO],
                caption: str,
                reply_to: int,
                url: str = None,
                parse_mode: ParseMode = ParseMode.HTML
        ) -> Message:
                print("[send_patch_email]")
                return await self.send_document(
			chat_id=chat_id,
                        document=doc,
			caption=caption,
			reply_to_message_id=reply_to,
			parse_mode=parse_mode,
			reply_markup=InlineKeyboardMarkup([
				[InlineKeyboardButton(
					"See the full message",
					url=url
				)]
			])
		)
