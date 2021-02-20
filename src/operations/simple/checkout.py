#!/usr/bin/env python3

import shutil
import json
from pathlib import Path

from input_parser import add_simple_operation
from core.simple_operation import SimpleOperation
from utils.exceptions import NotEmptyDirectory
from distutils.dir_util import copy_tree


class Checkout(SimpleOperation):
    def __init__(self, working_directory: str, remove_patches: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.no_patch = remove_patches
        self.working_dir = Path(working_directory)
        self.source = self.working_dir / Path(self.challenge.name)
        self.tracker_file = self.working_dir / ".tracker"
#        self.fl_file = self.working_dir / "__cheat.log" if fl_file else None
        self.compile_script = self.working_dir / Path("compile.sh")

    def __call__(self):
        # Make working directory
        self.status(f"Checking out {self.challenge.name} to {self.working_dir}.")

        try:
            self._mkdir()
            self.challenge.get_manifest()
            self._checkout_files()

            if self.no_patch:
                self.challenge.remove_patches(self.source)

            self._init_tracker()

            self.status(f"Checked out {self.challenge.name}", ok=True)
            return None, None
        except Exception as e:
            self.status(str(e), err=True)
            return None, str(e)

    def _init_tracker(self):
        with self.tracker_file.open(mode="w") as tf:
            init_data = {'name': self.challenge.name, 'outcomes': {}}
            json.dump(init_data, tf, indent=2)

    def _mkdir(self):
        if self.working_dir.exists():
            if any(self.working_dir.iterdir()):
                raise NotEmptyDirectory(f"Working directory {self.working_dir} exists and is not empty.")
        else:
            self.status("\tCreating working directory.")
            self.working_dir.mkdir(parents=True)

    def _checkout_files(self):
        self.status(f"\tCopying files to {self.working_dir}.")
        # Copy challenge source files
        self.source.mkdir()
        copy_tree(src=str(self.challenge.paths.source), dst=str(self.source))

        # Copy include libraries
        include_dest = self.working_dir / Path("include")
        include_dest.mkdir()
        copy_tree(src=str(self.get_lib_paths().root / Path("include")), dst=str(include_dest))
        tools = self.get_tools()
        # Copy CMakeLists.txt
        cmake_file = tools.cmake_file_no_patch if self.no_patch else tools.cmake_file
        dst_cmake_file = shutil.copy2(src=cmake_file, dst=self.working_dir)

        if self.no_patch:
            p_dst_cmake_file = Path(dst_cmake_file)
            p_dst_cmake_file.rename(Path(p_dst_cmake_file.parent, "CMakeLists.txt"))

        # Copy compile.sh script
        # shutil.copy2(src=tools.compile, dst=self.working_dir)

    def write_fl_file(self):
        if self.fl_file:
            _, manifest = self.challenge.get_manifest(force=True)

            with self.fl_file.open(mode="w") as flf:
                for file, vulns in manifest.get_vulns().items():
                    for start, vuln in vulns.items():
                        for i, line in enumerate(vuln):
                            column = line.find(line.strip()) + 1
                            full_path = self.source / file
                            loc = f"{full_path} {start+i} {column}"
                            flf.write(f"{loc} {loc}\n")


def checkout_args(input_parser):
    input_parser.add_argument('-rp', '--remove_patches', action='store_true',
                              help='Remove the patches and respective definitions from the source code.')
    input_parser.add_argument('-wd', '--working_directory', type=str, help='The working directory.', required=True)
#    input_parser.add_argument('--fl_file', action='store_true', help='File for fault localization info.')


co_parser = add_simple_operation("checkout", Checkout, 'Checks out challenge to working directory.')
checkout_args(co_parser)
