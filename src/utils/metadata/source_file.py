#!/usr/bin/env python3

import re
from pathlib import Path

from utils.metadata.snippet import Snippet

START = "^#(if|ifndef|ifdef) PATCHED"
CHANGE = "#else"
END = "#endif"


def line_indentation(line: str):
	return line[0:line.find(line.lstrip())] + "\n"


class SourceFile:
	def __init__(self, file_path: Path):
		self.path = file_path
		self.snippets = []

		with self.path.open(mode="r") as file:
			self.lines = file.readlines()

		self.total_lines = len(self.lines)
		self.removed = False
		self.vuln_lines = 0
		self.patch_lines = 0

		self.extract_snippets()

	def __len__(self):
		return len(self.snippets)

	def has_snippets(self):
		return len(self) > 0

	def extract_snippets(self):
		snippet = None

		for i, line in enumerate(self.lines):
			stripped = line.strip()
			if snippet is None:
				match = re.search(START, stripped)
				if match:
					snippet = Snippet(i)
					snippet(state="patch")
					self.snippets.append(snippet)
			else:
				if stripped.startswith(CHANGE):
					snippet.change = i
					snippet(state="vuln")
				elif stripped.startswith(END):
					snippet.end = i
					snippet = None
				else:
					snippet(line=line)

					if snippet.state == "patch":
						self.patch_lines += 1
					else:
						self.vuln_lines += 1

	def remove_patch(self):
		# copy of lines
		if self.removed:
			return

		aux_lines = self.lines.copy()
		shift = 0

		for snippet in self.snippets:
			if snippet.change is not None:
				patch_size = snippet.change - (snippet.start + 1)
				aux_lines[snippet.change] = None
				snippet.change -= (patch_size + 1 + shift)
			else:
				patch_size = snippet.end - (snippet.start + 1)

			if patch_size != 0:
				aux_lines[snippet.start] = line_indentation(aux_lines[snippet.start+1])
			else:
				aux_lines[snippet.start] = None

			aux_lines[snippet.start+1: snippet.start+1+patch_size] = [None] * patch_size
			aux_lines[snippet.end] = None
			snippet.start -= shift
			snippet.end -= (shift + patch_size + 1)
			shift += (patch_size + 1)

		with self.path.open(mode="w") as new_file:
			new_file.writelines(filter(None, aux_lines))
		self.removed = True

	def get_patch(self) -> dict:
		patch = {}

		for snippet in self.snippets:

			if snippet.change is not None:
				fix = self.lines[snippet.start+1:snippet.change]
			else:
				fix = self.lines[snippet.start+1:snippet.end]

			patch[snippet.start+1] = fix if fix else [' ']

		return patch

	def get_vuln_hunks(self) -> str:
		vuln_hunks = ""

		for snippet in self.snippets:
			if snippet.change:
				if snippet.start == snippet.end:
					vuln_hunks += f"{snippet.change+1},{snippet.end+1};"
				else:
					vuln_hunks += f"{snippet.change+1},{snippet.end};"
			else:
				if snippet.start == snippet.end:
					vuln_hunks += f"{snippet.start+1},{snippet.end+1};"
				else:
					vuln_hunks += f"{snippet.start+1},{snippet.end};"

		return vuln_hunks

	def get_vuln(self) -> dict:
		vuln = {}

		for snippet in self.snippets:

			if snippet.change is not None:
				lines = self.lines[snippet.change+1:snippet.end]
				vuln[snippet.change+1] = lines if lines else [' ']
			else:
				vuln[snippet.end+1] = [' ']

		return vuln
