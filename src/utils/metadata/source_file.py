#!/usr/bin/env python3

import re
from pathlib import Path

from utils.metadata.snippet import Snippet

START = "^#(if|ifndef|ifdef) PATCHED"
CHANGE = "#else"
END = "#endif"


class SourceFile:
	def __init__(self, file_path: Path):
		self.path = file_path
		self.snippets = []

		with self.path.open(mode="r") as file:
			self.lines = file.readlines()

		self.total_lines = len(self.lines)

		self.vuln_lines = 0
		self.patch_lines = 0

		self.extract_snippets()

	def __len__(self):
		return len(self.snippets)

	def has_snippets(self):
		return len(self) > 0

	def get_change(self):
		patch, vuln = [], []

		for snippet in self.snippets:
			patch.append(snippet.patch_range())

			if snippet.change:
				vuln.append(snippet.vuln_range())

		return patch, vuln

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

	def transform(self):
		for snippet in self.snippets:
			patch_size = snippet.change - snippet.start
			vuln_size = snippet.end - snippet.change

			for i in range(1, patch_size):
				self.lines[snippet.start+i] = f"+{self.lines[snippet.start+i]}"

			for i in range(1, vuln_size):
				self.lines[snippet.change+i] = f"-{self.lines[snippet.change+i]}"

		return self.lines

	def remove_patch(self):
		# copy of lines
		aux_lines = self.lines.copy()

		for snippet in self.snippets:
			if snippet.change is not None:
				patch_size = snippet.change - snippet.start
				aux_lines[snippet.change] = None
			else:
				patch_size = snippet.end - snippet.start

			for i in range(patch_size):
				aux_lines[snippet.start + i] = None

			aux_lines[snippet.end] = None

		with self.path.open(mode="w") as new_file:
			new_file.writelines(list(filter(None, aux_lines)))
