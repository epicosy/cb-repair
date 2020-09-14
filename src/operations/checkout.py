#!/usr/bin/env python3

import shutil
from pathlib import Path

from input_parser import add_operation
from context import Context
from utils.exceptions import NotEmptyDirectory
from distutils.dir_util import copy_tree


class Checkout(Context):
    def __init__(self,
                 remove_patches: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.no_patch = remove_patches
        self.compile_script = self.working_dir / Path("compile.sh")

    def __call__(self):
        # Make working directory
        self.status(f"Checking out {self.challenge.name} to {self.working_dir}.\n")
        self._mkdir()
        self._checkout_files()

        manifest = self.challenge.get_manifest(self.source)
        manifest.write()

        if self.no_patch:
            manifest.remove_patches()

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
        shutil.copy2(src=tools.compile, dst=self.working_dir)


def checkout_args(input_parser):
    input_parser.add_argument('-rp', '--remove_patches', action='store_true',
                              help='Remove the patches and respective definitions from the source code.')


co_parser = add_operation("checkout", Checkout, 'Checks out challenge to working directory.')
checkout_args(co_parser)
