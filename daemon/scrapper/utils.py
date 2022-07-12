# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from email.message import Message
from typing import Dict
import hashlib, os, uuid

def extract_list(key: str, content: Dict[str, str]):
	if not bool(content.get(key.lower())):
		return []
	return content[key.lower()].split(", ")

def consruct_to_n_cc(to: list, cc: list):
	template = ""

	for t in to[:10]:
		template += f"To: {t}\n"

	if len(to) >= 10:
		template += "To: ...\n"
		template += "Cc: ...\n" if len(cc) != 0 else ""

	elif len(cc) != 0:
		substr = 10 - len(to)

		for c in cc[:substr]:
			template += f"Cc: {c}\n"
		else:
			template += "Cc: ...\n"

	return template

def extract_body(thread: Message):
	if not thread.is_multipart():
		return f"{thread.get_payload(decode=True).decode()}\n".lstrip(), []

	ret = ""
	files = []
	temp = gen_temp(str(thread.get("message-id", uuid.uuid4())))

	for p in thread.get_payload():
		fname = p.get_filename()
		payload = p.get_payload(decode=True)

		if 'inline' in [p.get('content-disposition')] or not bool(fname):
			ret += f"{payload.decode()}\n".lstrip()
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
	) + "\n<code>------------------------------------------------------------------------</code>"

	return template, files

def gen_temp(name: str):
	md5 = hashlib.md5(name.encode()).hexdigest()
	os.mkdir(md5)
	return md5
