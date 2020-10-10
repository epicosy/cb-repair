#!/usr/bin/env python3

from functools import lru_cache
from typing import Dict, List, NoReturn
from pathlib import Path

from utils.metadata.source_file import SourceFile

EXTENSIONS = (".c", ".cc", ".h")
IGNORE = ("polls", "pov", "support")


class Manifest:
    def __init__(self, source_path: Path):
        self.root = source_path
        self.source_files: Dict[(str, SourceFile)] = {}
        self.vuln_files: Dict[(str, SourceFile)] = {}
        self.total_lines = 0
        self.vuln_lines = 0
        self.patch_lines = 0
        self.collect_files()

    def collect_files(self) -> NoReturn:
        def recurse_walk(current: Path, parent: Path):
            for f in current.iterdir():
                if f.is_dir():
                    recurse_walk(f, parent / Path(f.name))
                elif f.name.endswith(EXTENSIONS):
                    short_path = str(parent / Path(f.name))
                    src_file = SourceFile(f)
                    self.total_lines += src_file.total_lines

                    if src_file.has_snippets():
                        self.vuln_files[short_path] = src_file
                        self.vuln_lines += src_file.vuln_lines
                        self.patch_lines += src_file.patch_lines
                    else:
                        self.source_files[short_path] = src_file

        for folder in self.root.iterdir():
            if folder.name not in IGNORE and folder.is_dir():
                recurse_walk(folder, Path(folder.name))

    def remove_patches(self) -> NoReturn:
        for file in self.vuln_files.values():
            file.remove_patch()

    def write(self, out_file: Path = None, hunks: bool = False) -> NoReturn:
        out = out_file if out_file else self.root / Path("manifest.txt")

        with out.open(mode="w") as of:
            for short_file_path, vuln_file in self.vuln_files.items():
                if hunks:
                    # file_path:hunk_start,hunk_end;hunk_start,hunk_end;
                    vuln_hunks = vuln_file.get_vuln_hunks()
                    of.write(f"{short_file_path}:{vuln_hunks}\n")
                else:
                    of.write(short_file_path + "\n")

    # TODO: this might fail in cases where the header files have files associated
    def map_instrumented_files(self, instrumented_files: List[str], cpp_files: bool) -> Dict[(str, str)]:
        mapping = {}
        
        for short_path, file in self.vuln_files.items():
            if file.path.suffix == "h":
                continue
            if cpp_files:
                short_path = short_path.replace('.c', '.i')
            print(short_path)
            for inst_file in instrumented_files:
                if short_path in inst_file:
                    if cpp_files:
                        short_path = short_path.replace('.i', '.c')
                    mapping[short_path] = inst_file
                    break

        return mapping
