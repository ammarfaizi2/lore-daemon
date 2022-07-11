# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2022  Muhammad Rizki <riskimuhammmad1@gmail.com>
#

from email.message import Message
from typing import Dict
import hashlib, os, uuid, re

def extract_list(key: str, content: Dict[str, str]):
	if not bool(content.get(key.lower())):
		return []
	return content[key.lower()].split(", ")

def consruct_to_n_cc(to: list, cc: list):
	template = ""

	for t in to[:10]:
		template += f"To: {t}\n"

		if to.index(t) >= 10:
			template += "To: ..."

	if len(to) >= 10 and len(cc) != 0:
		template += "Cc: ...\n"

	elif len(cc) != 0:
		substr = 10 - len(to)

		for c in cc[:substr]:
			template += f"Cc: {c}\n"

			if cc.index(c) >= 10:
				template += "Cc: ..."

	return template

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
