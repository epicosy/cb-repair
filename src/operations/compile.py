#!/usr/bin/env python3

from os import environ
from pathlib import Path
from typing import List

from operations.make import Make, make_args
from input_parser import add_operation
from utils.metadata.manifest import map_instrumented_files


class Compile(Make):
    def __init__(self, inst_files: List[str] = None, fix_files: List[str] = None, cpp_files: bool = False,
                 coverage: bool = False, link: bool = False, backup: str = None , **kwargs):
        super().__init__(**kwargs)
        self._set_build_paths()
        self.inst_files = inst_files
        self.fixes = fix_files
        self.cpp_files = cpp_files
        self.coverage = coverage
        self.link = link
        self.backup = Path(backup) if backup else None

        if self.coverage:
            environ["COVERAGE"] = "True"

        self.set_env()

        if self.fixes and not isinstance(self.fixes, list):
            self.fixes = [self.fixes]

        self.log(str(self))

        if self.fixes and self.inst_files and len(self.fixes) != len(self.inst_files):
            self.outcome(1, f"The files with changes [{fix_files}] can not be mapped. Uneven number of files " +
                         f"[{inst_files}].")

    def __call__(self):
        try:
            # Backups manifest files
            if self.backup:
                self._backup_manifest_files()

            if self.link:
                self.status(f"Linking into executable {self.challenge.name}.")
                self.link_executable()
            elif self.inst_files:
                self.status(f"Compiling preprocessed file for {self.challenge.name}.")
                # compile the preprocessed file to object
                self.load_commands()
                mapping = map_instrumented_files(self.inst_files, cpp_files=self.cpp_files,
                                                 manifest_path=self.source / Path('manifest'))

                if not mapping:
                    self.outcome(1, f"Could not map fix files {self.fixes} with source files.")

                # creating object files
                for source_file, cpp_file in mapping.items():
                    self.build_file(source_file, cpp_file)

                # links objects into executable
                self.link_executable()
            else:
                self.status(f"Compiling {self.challenge.name}.")
                self._make()
                self._build()
        finally:
            if self.coverage:
                del environ['COVERAGE']
        self.status(f"Compiled {self.challenge.name}.", ok=True)
        return None, None

    def _backup_manifest_files(self):
        manifest_file, _ = self.challenge.get_manifest(source_path=self.source)
        with manifest_file.open(mode="r") as mf:
            files = mf.readlines()
            for file in files:
                file_path = Path(file)
                bckup_path = self.backup / file_path.parent
                
                if not bckup_path.exists():
                    bckup_path.mkdir(parents=True, exist_ok=True)

                bckup_file = bckup_path / f"{file_path.stem}_{self.cid.decode()}{file_path.suffix}"
                super(Make, self).__call__(cmd_str=f"cp {file} {bckup_file}", msg=f"Backup of manifest file {file} to {self.backup}.\n",
                                   cmd_cwd=str(self.source))

    def _make(self):
        super().__call__()

        if self.error:
            self.outcome(1, self.error)

    def _build(self):
        super(Make, self).__call__(cmd_str=f"cmake --build .", msg=f"Building {self.challenge.name}\n",
                                   cmd_cwd=self.build_root)

        if self.error:
            self.outcome(1, self.error)

        self.outcome(0)

    def build_file(self, source_file: str, cpp_file: str):
        if self.fixes:
            cpp_file = self.fixes.pop(0)

            if self.prefix:
                cpp_file = str(self.prefix / Path(cpp_file))

        if not Path(cpp_file).exists():
            self.outcome(1, f"File {cpp_file} not found.")

        compile_command = self.get_compile_command(source_file, cpp_file)
        super(Make, self).__call__(cmd_str=compile_command, msg=f"Creating object file for {cpp_file}.\n",
                                   cmd_cwd=str(self.build))

        if self.error:
            self.outcome(1, self.error)

    def link_executable(self):
        if not self.link_file.exists():
            self.outcome(1, "No link file found")
        else:
            cmd_str=f"cmake -E cmake_link_script {self.link_file} {self.challenge.name}"
            super(Make, self).__call__(cmd_str=cmd_str, msg="Linking object files into executable.\n",
                                       cmd_cwd=str(self.build))

            if self.error:
                self.outcome(1, self.error)

            self.outcome(0)

    def get_compile_command(self, manifest_file: str, instrumented_file: str = None):
        if manifest_file not in self.compile_commands:
            self.outcome(1, "Could not find compile command.")

        compile_command = self.compile_commands[manifest_file]
        modified_command = compile_command.command.replace('-save-temps=obj', '')

        if instrumented_file:
            modified_command = modified_command.replace(str(compile_command.file), instrumented_file)

        return modified_command

    def __str__(self):
        compile_cmd_str = ""

        if self.inst_files:
            compile_cmd_str += f" --inst_files {' '.join(self.inst_files)}"

        if self.fixes:
            compile_cmd_str += f" --fix_file {self.fixes}"

        return super().__str__() + compile_cmd_str + "\n"


def compile_args(input_parser):
    input_parser.add_argument('-ifs', '--inst_files', nargs='+', help='Instrumented files to compile.', default=None)
    input_parser.add_argument('--coverage', action='store_true', required=False, help='Cmake generates gcov files.')
    input_parser.add_argument('--link', action='store_true', required=False,
                              help='Flag for only links objects into executable.')
    input_parser.add_argument('-cpp', '--cpp_files', action='store_true', required=False,
                              help='Flag to indicate that instrumented files are preprocessed.')
    input_parser.add_argument('-ffs', '--fix_files', nargs='+', default=None,
                              help='The file with changes applied by the repair tool.')
    input_parser.add_argument('-B', '--backup', type=str, help='Backups the manifest file to a given path.', default=None)
    make_args(input_parser)


c_parser = add_operation("compile", Compile, 'Compiles challenge binary.')
compile_args(c_parser)
