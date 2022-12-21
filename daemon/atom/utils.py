# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from enums import Platform

from pyrogram.types import Chat, InlineKeyboardMarkup, InlineKeyboardButton
from email.message import Message
from typing import Dict, Union
from slugify import slugify
from base64 import b64decode
import hashlib
import uuid
import os
import re
import shutil
import httpx
import html
import quopri


def get_email_msg_id(mail):
	ret = mail.get("message-id")
	if not ret:
		return None

	ret = re.search(r"<([^\<\>]+)>", ret)
	if not ret:
		return None

	return ret.group(1)


#
# This increments the @i while we are seeing a whitespace.
#
def __skip_whitespace(i, ss_len, ss):
	while i < ss_len:
		c = ss[i]
		if c != ' ' and c != '\t' and c != '\n':
			break
		i += 1

	return i


#
# Pick a single element in the list. The delimiter here is
# a comma char ','. But note that when are inside a double
# quotes, we must not take the comma as a delimiter.
#
def __pick_element(i, ss_len, ss, ret):
	acc = ""
	in_quotes = False

	while i < ss_len:
		c = ss[i]
		i += 1

		if c == '"':
			in_quotes = (not in_quotes)

		if not in_quotes and c == ',':
			break

		acc += c

	if acc != "":
		ret.append(acc)

	return i


def __extract_list(ss):
	ss = ss.strip()
	ss_len = len(ss)
	ret = []
	i = 0

	while i < ss_len:
		i = __skip_whitespace(i, ss_len, ss)
		i = __pick_element(i, ss_len, ss, ret)

	return ret


def extract_list(key: str, content: Dict[str, str]):
	people = content.get(key.lower())
	if not people:
		return []
	return __extract_list(people)


def consruct_to_n_cc(to: list, cc: list):
	NR_MAX_LIST = 20

	n = 0
	ret = ""
	for i in to:
		if n >= NR_MAX_LIST:
			ret += "To: ...\n"
			break

		n += 1
		ret += f"To: {i}\n"

	for i in cc:
		if n >= NR_MAX_LIST:
			ret += "Cc: ...\n"
			break

		n += 1
		ret += f"Cc: {i}\n"

	return ret


def gen_temp(name: str, platform: Platform):
	platform: str = platform.value
	md5 = hashlib.md5(name.encode()).hexdigest()
	store_dir = os.getenv("STORAGE_DIR", "storage")
	platform = platform.replace("discord", "dscord")
	path = f"{platform}/{store_dir}/{md5}"

	try:
		os.mkdir(path)
	except FileExistsError:
		pass

	return path


def extract_body(thread: Message, platform: Platform):
	if not thread.is_multipart():
		p = get_decoded_payload(thread)

		if platform is Platform.DISCORD:
			p = quote_reply(p)

		return f"{p}\n".lstrip(), []

	ret = ""
	files = []
	for p in thread.get_payload():
		fname = p.get_filename()
		payload = p.get_payload(decode=True)

		if p.get_content_type() == "text/html":
			continue

		if not payload:
			continue

		if p.get_content_disposition() == 'inline' or not bool(fname):
			ret += f"{payload.decode(errors='replace')}\n".lstrip()
			continue

		temp = gen_temp(str(uuid.uuid4()), platform)
		with open(f"{temp}/{fname}", "wb") as f:
			f.write(payload)
			files.append((temp, fname))

	return ret, files



PATCH_PATTERN = r"^\[.*(?:patch|rfc).*?(?:(\d+)\/(\d+))?\](.+)"
def __is_patch(subject, content):
	x = re.search(PATCH_PATTERN, subject, re.IGNORECASE)
	if not x or x.group(1) == "0":
		return False

	x = re.search(r"diff --git", content)
	if not x:
		return False

	return True


def create_template(thread: Message, platform: Platform, to=None, cc=None):
	if not to:
		to = extract_list("to", thread)
	if not cc:
		cc = extract_list("cc", thread)
	if platform is Platform.TELEGRAM:
		substr = 4000
		border = f"\n<code>{'-'*72}</code>"
	else:
		substr = 1900
		border = f"\n{'-'*80}"

	subject = thread.get('subject')
	ret = f"From: {thread.get('from')}\n"
	ret += consruct_to_n_cc(to, cc)
	ret += f"Date: {thread.get('date')}\n"
	ret += f"Subject: {subject}\n\n"
	content, files = extract_body(thread, platform)
	is_patch = __is_patch(subject, content)

	if is_patch:
		ret += content
	else:
		ret += content.strip().replace("\t", "        ")

		if len(ret) >= substr:
			ret = ret[:substr] + "..."

		ret = fix_utf8_char(ret, platform is Platform.TELEGRAM)
		ret += border

	return ret, files, is_patch


def prepare_patch(mail: Message, text, url, platform: Platform):
	tmp = gen_temp(url, platform)
	fnm = str(mail.get("subject"))
	sch = re.search(PATCH_PATTERN, fnm, re.IGNORECASE)

	nr_patch = sch.group(1)
	if not nr_patch:
		nr_patch = 1
	else:
		nr_patch = int(nr_patch)

	num = "%04d" % nr_patch
	fnm = slugify(sch.group(3)).replace("_", "-")
	file = f"{tmp}/{num}-{fnm}.patch"
	cap = text.split("\n\n")[0]

	with open(file, "wb") as f:
		write_payload = bytes(f"{cap}\n\n".encode())

		# sometimes an email PATCH is a multipart
		# so, we must loop the payload first
		# then, check if each payload is a PATCH payload
		# or no, if it's a PATCH payload then write payload
		# to the file.
		if mail.is_multipart():
			for m in mail.get_payload():
				subject = mail.get("subject")
				if not __is_patch(subject, str(m)):
					continue
				write_payload += m.get_payload(decode=True)
		else:
			write_payload += mail.get_payload(decode=True)

		f.write(write_payload)

	caption = f"#patch #ml\n{cap}"
	if platform is Platform.TELEGRAM:
		# Telegram media caption is limit to 1024
		# set limit to 1021, because we will add "..."
		if len(caption) >= 1024:
			caption = caption[:1021] + "..."

		fixed = fix_utf8_char(caption, html_escape=True)
		return tmp, file, fixed, url

	# Discord attachment caption limit about 1998 or 2000
	# set limit to 1995, because we will add "..."
	if len(caption) >= 1998:
		caption = caption[:1995] + "..."

	return tmp, file, caption, url


def remove_patch(tmp: Union[str, list]):
	if isinstance(tmp, str):
		return shutil.rmtree(tmp)

	for d,_ in tmp:
		shutil.rmtree(d)


def fix_utf8_char(text: str, html_escape: bool = True):
	t = text.rstrip().replace("�"," ")
	if html_escape:
		t = html.escape(html.escape(text))
	return t


def get_decoded_payload(payload: Message):
	p = str(payload.get_payload())
	tf_encode = payload.get("Content-Transfer-Encoding")
	charset = payload.get_content_charset("utf-8")

	if tf_encode == "base64":
		return b64decode(p).decode(charset)
	if tf_encode == "quoted-printable":
		quobyte = quopri.decodestring(p.encode())
		return quobyte.decode(charset)

	return p.encode().decode(charset, errors="replace")


EMAIL_MSG_ID_PATTERN = r"<([^\<\>]+)>"
def extract_email_msg_id(msg_id):
	ret = re.search(EMAIL_MSG_ID_PATTERN, msg_id)
	if not ret:
		return None
	return ret.group(1)


async def is_atom_url(text: str):
	try:
		async with httpx.AsyncClient() as ses:
			res = await ses.get(text)
			mime = res.headers.get("Content-Type")

			return mime == "application/atom+xml"
	except: return False

def quote_reply(text: str):
	a = ""
	for b in text.split("\n"):
		b = b.replace(">\n", "> ")
		if b.startswith(">"):
			a += "> "
		a += f"{b}\n"
	return a

def remove_command(text: str):
	txt = text.split(" ")
	txt = text.replace(txt[0] + " ","")
	return txt


def button_numbers(data: list, callback_prefix: str, limit: int = 8):
	if limit > 8:
		raise ValueError("Limit value cannot more than 8.")

	lst = []
	for i in range(1, len(data)+1):
		button = InlineKeyboardButton(
			str(i),
			callback_data=f"{callback_prefix} {i}"
		)
		lst.append(button)

	buttons = [lst[i:i + limit ] for i in range(0, len(lst), limit)]
	return InlineKeyboardMarkup(buttons)


def create_chat_link(chat: Chat):
	if chat.invite_link:
		return chat.invite_link

	if chat.username:
		return f"t.me/{chat.username}"

	chat_id_str = str(chat.id).replace("-100","")
	return f"t.me/c/{chat_id_str}/1"


def channel_link(guild_id: int, channel_id: int):
	return f"https://discord.com/channels/{guild_id}/{channel_id}"
