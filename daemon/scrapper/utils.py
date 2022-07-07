from email.message import Message
from typing import Dict
import re

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
	for p in thread.get_payload():
		if 'inline' in [p.get('content-disposition')] or not bool(p.get_filename()):
			ret += f"{p.get_payload(decode=True).decode()}\n".lstrip()
			continue

		with open(p.get_filename(), "wb") as f:
			f.write(p.get_payload(decode=True))
			files.append(p.get_filename())

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
