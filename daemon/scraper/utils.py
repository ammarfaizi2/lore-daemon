# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
# Copyright (C) 2022  Ammar Faizi <ammarfaizi2@gnuweeb.org>
#

from email.message import Message
from typing import Dict
import hashlib
import uuid
import os
import re


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

		ret = (
			ret.rstrip()
			.replace("<", "&lt;")
			.replace(">","&gt;")
			.replace("�"," ")
		) + "\n<code>------------------------------------------------------------------------</code>"

	return ret, files, is_patch


EMAIL_MSG_ID_PATTERN = r"<([^\<\>]+)>"
def extract_email_msg_id(msg_id):
	ret = re.search(EMAIL_MSG_ID_PATTERN, msg_id)
	if not ret:
		return None
	return ret.group(1)

