# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from email.message import Message
from typing import Dict
import hashlib, os, uuid, re

#
# This increments the @i while we are seeing a whitespace.
#
def _skip_whitespace(i, ss_len, ss):
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
def _pick_element(i, ss_len, ss, ret):
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

def _extract_list(ss):
	ss = ss.strip()
	ss_len = len(ss)
	ret = []
	i = 0

	while i < ss_len:
		i = _skip_whitespace(i, ss_len, ss)
		i = _pick_element(i, ss_len, ss, ret)

	return ret

def extract_list(key: str, content: Dict[str, str]):
	people = content.get(key.lower())
	if not people:
		return []
	return _extract_list(people)

def consruct_to_n_cc(to: list, cc: list):
	NR_MAX_LIST = 10

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

def create_template(thread: Message):
	to = extract_list("to", thread)
	cc = extract_list("cc", thread)

	template = f"From: {thread.get('from')}\n"
	template += consruct_to_n_cc(to, cc)
	template += f"Date: {thread.get('date')}\n"
	template += f"Subject: {thread.get('subject')}\n\n"

	content, files = extract_body(thread)
	template += content

	template = (
		template[:4000]
		.rstrip()
		.replace("<", "&lt;")
		.replace(">","&gt;")
		.replace("�"," ")
	) + "\n<code>------------------------------------------------------------------------</code>"

	return template, files

def gen_temp(name: str):
	md5 = hashlib.md5(name.encode()).hexdigest()
	os.mkdir(md5)
	return md5

def extract_email_id(text: str):
	return re.search(r"<([^\<\>]+)>", text).group(1)

def email_id_from_url(text: str):
	return text.split("/")[-2]

def get_reply_to(thread, db):
	reply_to = None
	in_reply_to = thread.get("in-reply-to")

	if in_reply_to:
		in_reply_id = utils.extract_email_id(str(in_reply_to))
		reply_to = db.reply_to(in_reply_id)

