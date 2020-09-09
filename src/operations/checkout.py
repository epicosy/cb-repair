#!/usr/bin/env python3

import shutil
from pathlib import Path

from input_parser import add_operation
from operation import Operation
from utils.streams import copytree
from utils.exceptions import NotEmptyDirectory


class Checkout(Operation):
    def __init__(self,
                 name: str,
                 source: bool = False,
                 remove_patches: bool = False,
                 **kwargs):
        super().__init__(name, **kwargs)
        self.src = source
        self.no_patch = remove_patches
        self.compile_script = self.working_dir / Path("compile.sh")

    def __call__(self):
        # Make working directory
        self.status(f"Checking out {self.challenge.name} to {self.working_dir}.\n")
        self._mkdir()
        self._checkout_files()

        if self.no_patch:
            self._remove_patches()

    def _mkdir(self):
        if self.working_dir.exists():
            if any(self.working_dir.iterdir()):
                raise NotEmptyDirectory(f"Working directory {self.working_dir} exists and is not empty.")
        else:
            self.status("Creating working directory.\n")
            self.working_dir.mkdir()

    def _checkout_files(self):
        self.status(f"Copying files to {self.working_dir}.")
        # Copy challenge source files
        self.source.mkdir()
        copytree(src=self.challenge.paths.source, dst=self.source)

        # Copy include libraries
        (self.working_dir / Path("include")).mkdir()
        copytree(src=self.get_lib_paths().root / Path("include"),
                 dst=self.working_dir / Path("include"))
        tools = self.get_tools()
        # Copy CMakeLists.txt
        cmake_file = tools.cmake_file_no_patch if self.no_patch else tools.cmake_file
        dst_cmake_file = shutil.copy2(src=cmake_file, dst=self.working_dir)

        if self.no_patch:
            p_dst_cmake_file = Path(dst_cmake_file)
            p_dst_cmake_file.rename(Path(p_dst_cmake_file.parent, "CMakeLists.txt"))

        # Copy compile.sh script
        shutil.copy2(src=tools.compile, dst=self.working_dir)

    def _remove_patches(self):
        manifest = self.challenge.get_manifest(self.source)
        manifest.remove_patches()


def checkout_args(input_parser):
    input_parser.add_argument('-rp', '--remove_patches', action='store_true',
                              help='Remove the patches and respective definitions from the source code.')


co_parser = add_operation("checkout", Checkout, 'Checks out challenge to working directory.')
checkout_args(co_parser)
