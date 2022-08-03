# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from pyrogram.types import Chat, InlineKeyboardMarkup, InlineKeyboardButton
from email.message import Message
from typing import Dict
from slugify import slugify
import hashlib
import uuid
import os
import re
import shutil
import httpx


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


def gen_temp(name: str):
	md5 = hashlib.md5(name.encode()).hexdigest()
	ret = os.getenv("STORAGE_DIR", "storage") + "/" + md5
	try:
		os.mkdir(ret)
	except FileExistsError:
		pass

	return ret


def extract_body(thread: Message):
	if not thread.is_multipart():
		p = thread.get_payload(decode=True)
		return f"{p.decode(errors='replace')}\n".lstrip(), []

	ret = ""
	files = []
	temp = gen_temp(str(uuid.uuid4()))
	for p in thread.get_payload():
		fname = p.get_filename()
		payload = p.get_payload(decode=True)

		if not payload:
			continue

		if 'inline' in [p.get('content-disposition')] or not bool(fname):
			ret += f"{payload.decode(errors='replace')}\n".lstrip()
			continue

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


def create_template(thread: Message, to=None, cc=None):
	if not to:
		to = extract_list("to", thread)
	if not cc:
		cc = extract_list("cc", thread)

	subject = thread.get('subject')
	ret = f"From: {thread.get('from')}\n"
	ret += consruct_to_n_cc(to, cc)
	ret += f"Date: {thread.get('date')}\n"
	ret += f"Subject: {subject}\n\n"
	content, files = extract_body(thread)
	is_patch = __is_patch(subject, content)

	if is_patch:
		ret += content
	else:
		ret += content.strip().replace("\t", "        ")
		if len(ret) >= 4000:
			ret = ret[:4000] + "..."

		ret = fix_utf8_char(ret)
		ret += f"\n<code>{'-'*72}</code>"

	return ret, files, is_patch


def prepare_send_patch(mail, text, url):
	tmp = gen_temp(url)
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
		f.write(bytes(text, encoding="utf8"))

	caption = "#patch #ml\n" + fix_utf8_char(cap)
	return tmp, file, caption, url


def clean_up_after_send_patch(tmp):
	shutil.rmtree(tmp)


def fix_utf8_char(text: str):
	return (
		text.rstrip()
		.replace("<", "&lt;")
		.replace(">","&gt;")
		.replace("�"," ")
	)


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
